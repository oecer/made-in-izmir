from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignUpForm, CustomLoginForm, ProfileEditForm, TenantLogoRequestForm, TenantPhotoRequestForm
from .models import MembershipConsent, ConsentText, TenantPhoto


def _get_client_ip(request):
    """Extract real client IP, respecting common proxy headers."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '0.0.0.0')


def signup_view(request):
    """User registration view - creates signup request for admin approval"""
    if request.user.is_authenticated:
        return redirect('main:index')

    consent_text = ConsentText.get_solo()

    if request.method == 'POST':
        consent_given = request.POST.get('membership_consent') == 'on'
        form = SignUpForm(request.POST)

        if not consent_given:
            messages.error(request, 'Devam etmek için üyelik onay metnini kabul etmelisiniz.')
            return render(request, 'auth/signup.html', {'form': form, 'consent_text': consent_text})

        if form.is_valid():
            from django.utils import timezone as tz
            now = tz.now()
            ip = _get_client_ip(request)

            signup_request = form.save()

            signup_request.consent_given = True
            signup_request.consent_timestamp = now
            signup_request.consent_ip = ip
            signup_request.save(update_fields=['consent_given', 'consent_timestamp', 'consent_ip'])

            MembershipConsent.objects.create(
                signup_request=signup_request,
                username=signup_request.username,
                email=signup_request.email,
                company_name=signup_request.company_name,
                consent_given_at=now,
                ip_address=ip,
                consent_text_version=consent_text.version,
            )

            return render(request, 'auth/signup.html', {
                'form': SignUpForm(),
                'consent_text': consent_text,
                'signup_success': True,
            })
        else:
            messages.error(request, 'Lütfen formdaki hataları düzeltiniz.')
    else:
        form = SignUpForm()

    return render(request, 'auth/signup.html', {'form': form, 'consent_text': consent_text})


def login_view(request):
    """User login view - accepts username OR email"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        login_identifier = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=login_identifier, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Hoş geldiniz, {user.get_full_name() or user.username}!')
            next_url = request.GET.get('next', 'accounts:dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Kullanıcı adı/e-posta veya şifre hatalı.')
            form = CustomLoginForm()
    else:
        form = CustomLoginForm()

    return render(request, 'auth/login.html', {'form': form})


@login_required
def logout_view(request):
    """User logout view"""
    logout(request)
    return redirect('main:index')


@login_required
def profile_view(request):
    """User profile view"""
    return render(request, 'auth/profile.html')


@login_required
def edit_profile_view(request):
    """Edit user profile view - creates edit request for admin approval"""
    try:
        profile = request.user.profile
    except Exception:
        messages.error(request, 'Profil bilgileriniz bulunamadı.')
        return redirect('main:index')

    if profile.tenant_role == 'read_only':
        messages.error(request, 'Salt okunur kullanıcılar profil düzenleyemez.')
        return redirect('accounts:profile')

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Profil düzenleme talebiniz alındı! Değişiklikler yönetici onayından sonra aktif hale gelecektir.'
            )
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Lütfen formdaki hataları düzeltin.')
    else:
        form = ProfileEditForm(user=request.user)

    return render(request, 'auth/edit_profile.html', {'form': form, 'profile': profile})


@login_required
def dashboard_view(request):
    """Main dashboard landing page"""
    try:
        profile = request.user.profile
        return render(request, 'user_area/dashboard.html', {'profile': profile, 'tenant': profile.tenant})
    except Exception:
        messages.error(request, 'Profil bilgileriniz bulunamadı.')
        return redirect('main:index')


def company_profile_view(request, company_username):
    """Public company profile/showroom page."""
    from django.shortcuts import get_object_or_404
    from django.http import Http404
    from catalog.models import Product
    from .models import Tenant

    tenant = get_object_or_404(Tenant, company_username=company_username)

    if not tenant.show_company_profile:
        raise Http404("Bu firma profili mevcut değil.")

    is_tenant_admin = False
    has_pending_logo = tenant.logo_requests.filter(status='pending').exists()
    pending_photo_count = 0

    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            if profile.tenant == tenant and profile.tenant_role == 'admin':
                is_tenant_admin = True
                pending_photo_count = tenant.photo_requests.filter(status='pending').count()
        except Exception:
            pass

    gallery_photos = tenant.gallery_photos.all()
    products = Product.objects.filter(tenant=tenant, is_active=True, in_showroom=True).order_by('-created_at')

    context = {
        'tenant': tenant,
        'gallery_photos': gallery_photos,
        'products': products,
        'is_tenant_admin': is_tenant_admin,
        'has_pending_logo': has_pending_logo,
        'pending_photo_count': pending_photo_count,
    }
    return render(request, 'company_profile/company_profile.html', context)


@login_required
def submit_company_logo_view(request):
    """Handles logo submission for approval."""
    from django.http import JsonResponse

    if request.method != 'POST':
        return JsonResponse({'error': 'Geçersiz istek.'}, status=405)

    try:
        profile = request.user.profile
    except Exception:
        return JsonResponse({'error': 'Profil bulunamadı.'}, status=403)

    if profile.tenant_role != 'admin':
        return JsonResponse({'error': 'Yetkiniz yok.'}, status=403)

    tenant = profile.tenant
    if not tenant:
        return JsonResponse({'error': 'Firma bulunamadı.'}, status=403)

    # Only one pending logo request at a time
    if tenant.logo_requests.filter(status='pending').exists():
        return JsonResponse({'error': 'Zaten onay bekleyen bir logo talebiniz var.'}, status=400)

    form = TenantLogoRequestForm(request.POST, request.FILES)
    if form.is_valid():
        logo_request = form.save(commit=False)
        logo_request.tenant = tenant
        logo_request.submitted_by = request.user
        logo_request.status = 'pending'
        logo_request.save()

        return JsonResponse({'success': True, 'message': 'Logonuz yönetici onayına gönderildi.'})

    return JsonResponse({'error': str(form.errors)}, status=400)


@login_required
def submit_gallery_photo_view(request):
    """Handles gallery photo submission for approval."""
    from django.http import JsonResponse

    if request.method != 'POST':
        return JsonResponse({'error': 'Geçersiz istek.'}, status=405)

    try:
        profile = request.user.profile
    except Exception:
        return JsonResponse({'error': 'Profil bulunamadı.'}, status=403)

    if profile.tenant_role != 'admin':
        return JsonResponse({'error': 'Yetkiniz yok.'}, status=403)

    tenant = profile.tenant
    if not tenant:
        return JsonResponse({'error': 'Firma bulunamadı.'}, status=403)

    if TenantPhoto.objects.filter(tenant=tenant).count() >= 10:
        return JsonResponse({'error': 'Maksimum 10 galeri fotoğrafı yükleyebilirsiniz.'}, status=400)

    form = TenantPhotoRequestForm(request.POST, request.FILES)
    if form.is_valid():
        photo_request = form.save(commit=False)
        photo_request.tenant = tenant
        photo_request.submitted_by = request.user
        photo_request.status = 'pending'
        photo_request.save()
        return JsonResponse({'success': True, 'message': 'Fotoğrafınız yönetici onayına gönderildi.'})

    return JsonResponse({'error': str(form.errors)}, status=400)
