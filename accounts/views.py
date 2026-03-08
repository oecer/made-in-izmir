from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignUpForm, CustomLoginForm, ProfileEditForm
from .models import MembershipConsent, ConsentText


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
