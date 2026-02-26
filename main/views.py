from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignUpForm, CustomLoginForm, ProductForm, ExpoSignupForm
from .models import Product, ProductTag, ProductRequest, Expo, ExpoSignup, UserProfile, Sector, MembershipConsent, ConsentText


def index(request):
    """Home page view - includes upcoming expos preview"""
    from django.utils import timezone as tz
    today = tz.now().date()
    upcoming_expos = Expo.objects.filter(is_active=True, start_date__gte=today).order_by('start_date')[:3]
    return render(request, 'index.html', {'upcoming_expos': upcoming_expos})


def about(request):
    """About page view"""
    return render(request, 'about.html')


def why_izmir(request):
    """Why Izmir page view"""
    return render(request, 'why_izmir.html')


def producers(request):
    """Producers page view"""
    return render(request, 'producers.html')


def buyers(request):
    """Buyers page view"""
    return render(request, 'buyers.html')


def calendar(request):
    """Calendar page view - public view of all expos"""
    from django.utils import timezone
    
    # Get all active expos, ordered by start date
    expos = Expo.objects.filter(is_active=True).order_by('start_date')
    
    # Separate upcoming and past expos
    today = timezone.now().date()
    upcoming_expos = expos.filter(start_date__gte=today)
    past_expos = expos.filter(start_date__lt=today)
    
    context = {
        'upcoming_expos': upcoming_expos,
        'past_expos': past_expos,
    }
    
    return render(request, 'calendar.html', context)


def contact(request):
    """Contact page view - handles both GET (render) and POST (form submission)"""
    if request.method == 'POST':
        name    = request.POST.get('name', '').strip()
        email   = request.POST.get('email', '').strip()
        phone   = request.POST.get('phone', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        # Basic server-side guard
        if not name or not email or not subject or not message:
            from django.http import HttpResponse
            return HttpResponse(status=400)

        # Try to send email; fail gracefully
        try:
            from django.core.mail import send_mail
            from django.conf import settings

            subject_line = f"[Made in İzmir] İletişim: {subject} - {name}"
            body = (
                f"Ad Soyad: {name}\n"
                f"E-posta:  {email}\n"
                f"Telefon:  {phone or '-'}\n"
                f"Konu:     {subject}\n\n"
                f"Mesaj:\n{message}"
            )
            send_mail(
                subject_line,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],  # send to site admin email
                fail_silently=False,
            )
        except Exception:
            # Email failed - return 500 so JS shows error banner
            from django.http import HttpResponse
            return HttpResponse(status=500)

        from django.http import HttpResponse
        return HttpResponse(status=200)

    return render(request, 'contact.html')


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

    consent_text = ConsentText.get_solo()  # singleton – never None

    if request.method == 'POST':
        # Consent checkbox must be ticked (second confirmation happens via JS popup)
        consent_given = request.POST.get('membership_consent') == 'on'
        form = SignUpForm(request.POST)

        if not consent_given:
            messages.error(request, 'Devam etmek için üyelik onay metnini kabul etmelisiniz.')
            return render(request, 'auth/signup.html', {'form': form, 'consent_text': consent_text})

        if form.is_valid():
            from django.utils import timezone as tz
            now = tz.now()
            ip = _get_client_ip(request)

            # form.save() already calls SignupRequest.objects.create() internally
            signup_request = form.save()

            # Patch consent fields and save again (single extra UPDATE query)
            signup_request.consent_given = True
            signup_request.consent_timestamp = now
            signup_request.consent_ip = ip
            signup_request.save(update_fields=['consent_given', 'consent_timestamp', 'consent_ip'])

            # Write permanent, immutable consent audit record
            MembershipConsent.objects.create(
                signup_request=signup_request,
                username=signup_request.username,
                email=signup_request.email,
                company_name=signup_request.company_name,
                consent_given_at=now,
                ip_address=ip,
                consent_text_version=consent_text.version,  # tracks live version
            )

            return render(request, 'auth/signup.html', {
                'form': SignUpForm(),           # fresh empty form
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
        return redirect('main:dashboard')
    
    if request.method == 'POST':
        # Get the raw login identifier (username or email) and password
        login_identifier = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        # authenticate() will call our custom backend which tries username then email
        user = authenticate(request, username=login_identifier, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Hoş geldiniz, {user.get_full_name() or user.username}!')
            next_url = request.GET.get('next', 'main:dashboard')
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
    from .forms import ProfileEditForm
    
    try:
        profile = request.user.profile
    except:
        messages.error(request, 'Profil bilgileriniz bulunamadı.')
        return redirect('main:index')
    
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, user=request.user)
        if form.is_valid():
            edit_request = form.save()
            messages.success(
                request,
                'Profil düzenleme talebiniz alındı! Değişiklikler yönetici onayından sonra aktif hale gelecektir.'
            )
            return redirect('main:profile')
        else:
            messages.error(request, 'Lütfen formdaki hataları düzeltin.')
    else:
        form = ProfileEditForm(user=request.user)
    
    context = {
        'form': form,
        'profile': profile
    }
    
    return render(request, 'auth/edit_profile.html', context)


@login_required
def dashboard_view(request):
    """Main dashboard landing page"""
    try:
        profile = request.user.profile
        return render(request, 'user_area/dashboard.html', {'profile': profile})
    except:
        messages.error(request, 'Profil bilgileriniz bulunamadı.')
        return redirect('main:index')


@login_required
def producer_dashboard_view(request):
    """Producer dashboard view"""
    try:
        profile = request.user.profile
        if not profile.is_producer:
            messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
            return redirect('main:dashboard')
        
        # Get filter parameters (support multiple values)
        status_filters = request.GET.getlist('status')
        tag_filters = [t for t in request.GET.getlist('tag') if t]
        sector_filters = [s for s in request.GET.getlist('sector') if s]
        search_query = request.GET.get('search', '').strip()
        
        # Get base querysets
        products_qs = Product.objects.filter(producer=request.user)
        requests_qs = ProductRequest.objects.filter(producer=request.user, status='pending')
        
        # Apply Search Filter
        if search_query:
            from django.db.models import Q
            products_qs = products_qs.filter(
                Q(title_tr__icontains=search_query) |
                Q(title_en__icontains=search_query) |
                Q(description_tr__icontains=search_query) |
                Q(description_en__icontains=search_query)
            )
            requests_qs = requests_qs.filter(
                Q(title_tr__icontains=search_query) |
                Q(title_en__icontains=search_query) |
                Q(description_tr__icontains=search_query) |
                Q(description_en__icontains=search_query)
            )
        
        # Determine available tags and sectors for the producer (for dropdowns)
        prod_product_tag_ids = products_qs.values_list('tags', flat=True)
        prod_request_tag_ids_str = requests_qs.values_list('tags_ids', flat=True)
        
        all_prod_tag_ids = set(tid for tid in prod_product_tag_ids if tid)
        for tags_str in prod_request_tag_ids_str:
            if tags_str:
                all_prod_tag_ids.update(int(tid) for tid in tags_str.split(',') if tid.strip().isdigit())
        
        available_tags = ProductTag.objects.filter(id__in=all_prod_tag_ids).distinct()
        
        prod_product_sector_ids = products_qs.values_list('sector_id', flat=True)
        prod_request_sector_ids = requests_qs.values_list('sector_id', flat=True)
        all_prod_sector_ids = set(sid for sid in prod_product_sector_ids if sid) | set(sid for sid in prod_request_sector_ids if sid)
        
        available_sectors = Sector.objects.filter(id__in=all_prod_sector_ids).distinct()

        # Apply Status Filters
        if status_filters:
            has_active = 'active' in status_filters
            has_passive = 'passive' in status_filters
            has_pending = 'pending' in status_filters
            
            if not has_pending:
                requests_qs = requests_qs.none()
            
            if has_active and not has_passive:
                products_qs = products_qs.filter(is_active=True)
            elif has_passive and not has_active:
                products_qs = products_qs.filter(is_active=False)
            elif not has_active and not has_passive:
                products_qs = products_qs.none()
        
        # Apply Sector Filters
        if sector_filters:
            products_qs = products_qs.filter(sector_id__in=sector_filters)
            requests_qs = requests_qs.filter(sector_id__in=sector_filters)
        
        # Apply Tag Filters
        if tag_filters:
            products_qs = products_qs.filter(tags__id__in=tag_filters).distinct()
            # For requests, filter the list: check if any of the selected tags match the request's tags
            selected_tag_set = set(str(t) for t in tag_filters)
            request_list = []
            for r in requests_qs:
                r_tags = (r.tags_ids or '').split(',')
                if any(t.strip() in selected_tag_set for t in r_tags if t.strip()):
                    request_list.append(r)
        else:
            request_list = list(requests_qs)

        # Unify Products and Requests
        display_items = list(products_qs)
        for req in request_list:
            req.is_pending = True
            display_items.append(req)
        
        # Sort by creation date
        display_items.sort(key=lambda x: x.created_at, reverse=True)
        
        # Stats (unfiltered for the stats cards)
        unfiltered_products = Product.objects.filter(producer=request.user)
        pending_count = ProductRequest.objects.filter(producer=request.user, status='pending').count()
        
        context = {
            'profile': profile,
            'products': display_items,
            'total_products': unfiltered_products.count() + pending_count,
            'active_products': unfiltered_products.filter(is_active=True).count(),
            'pending_products_count': pending_count,
            'available_tags': available_tags,
            'available_sectors': available_sectors,
            'current_filters': {
                'status': status_filters,
                'tag': tag_filters,
                'sector': sector_filters,
            },
            'search_query': search_query,
        }
        
        return render(request, 'user_area/producer_dashboard.html', context)
    except UserProfile.DoesNotExist:
        messages.error(request, 'Profil bilgileriniz bulunamadı.')
        return redirect('main:index')
    except Exception as e:
        messages.error(request, f'Sistem hatası: {str(e)}')
        return redirect('main:dashboard')


@login_required
def buyer_dashboard_view(request):
    """Buyer dashboard view"""
    try:
        profile = request.user.profile
        if not profile.is_buyer:
            messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
            return redirect('main:dashboard')
        
        # Get filter parameters (support multiple values)
        tag_filters = [t for t in request.GET.getlist('tag') if t]
        sector_filters = [s for s in request.GET.getlist('sector') if s]
        producer_filters = [p for p in request.GET.getlist('producer') if p]
        search_query = request.GET.get('search', '').strip()
        
        # Get all active products (buyers can browse products)
        products_qs = Product.objects.filter(is_active=True)
        
        # Apply Search Filter
        if search_query:
            from django.db.models import Q
            products_qs = products_qs.filter(
                Q(title_tr__icontains=search_query) |
                Q(title_en__icontains=search_query) |
                Q(description_tr__icontains=search_query) |
                Q(description_en__icontains=search_query)
            )
        
        # Apply Sector Filters
        if sector_filters:
            products_qs = products_qs.filter(sector_id__in=sector_filters)
        
        # Apply Tag Filters
        if tag_filters:
            products_qs = products_qs.filter(tags__id__in=tag_filters).distinct()
        
        # Apply Producer Filters
        if producer_filters:
            products_qs = products_qs.filter(producer_id__in=producer_filters)
        
        # Order by creation date
        products_qs = products_qs.order_by('-created_at')
        
        # Get available filters (all active products)
        all_active_products = Product.objects.filter(is_active=True)
        
        # Available tags
        available_tag_ids = all_active_products.values_list('tags', flat=True).distinct()
        available_tags = ProductTag.objects.filter(id__in=available_tag_ids).distinct()
        
        # Available sectors
        available_sector_ids = all_active_products.values_list('sector_id', flat=True).distinct()
        available_sectors = Sector.objects.filter(id__in=available_sector_ids).distinct()
        
        # Available producers (users who have active products)
        from django.contrib.auth.models import User
        available_producer_ids = all_active_products.values_list('producer_id', flat=True).distinct()
        available_producers = User.objects.filter(id__in=available_producer_ids).select_related('profile')
        
        context = {
            'profile': profile,
            'products': products_qs,
            'total_products': all_active_products.count(),
            'total_producers': available_producers.count(),
            'total_sectors': available_sectors.count(),
            'available_tags': available_tags,
            'available_sectors': available_sectors,
            'available_producers': available_producers,
            'current_filters': {
                'tag': tag_filters,
                'sector': sector_filters,
                'producer': producer_filters,
            },
            'search_query': search_query,
        }
        
        return render(request, 'user_area/buyer_dashboard.html', context)
    except:
        messages.error(request, 'Profil bilgileriniz bulunamadı.')
        return redirect('main:index')


@login_required
def add_product_view(request):
    """Add new product view (producers only) - creates product request for admin approval"""
    try:
        profile = request.user.profile
        if not profile.is_producer:
            messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
            return redirect('main:dashboard')
    except:
        messages.error(request, 'Profil bilgileriniz bulunamadı.')
        return redirect('main:index')
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            # Get tag IDs as comma-separated string
            tags = form.cleaned_data.get('tags', [])
            tag_ids = ','.join(str(tag.id) for tag in tags) if tags else ''
            
            # Create product request instead of product
            product_request = ProductRequest.objects.create(
                producer=request.user,
                sector=form.cleaned_data.get('sector'),
                title_tr=form.cleaned_data.get('title_tr', ''),
                title_en=form.cleaned_data.get('title_en', ''),
                description_tr=form.cleaned_data.get('description_tr', ''),
                description_en=form.cleaned_data.get('description_en', ''),
                photo1=form.cleaned_data.get('photo1'),
                photo2=form.cleaned_data.get('photo2'),
                photo3=form.cleaned_data.get('photo3'),
                tags_ids=tag_ids,
                is_active=form.cleaned_data.get('is_active', True),
                status='pending'
            )
            
            messages.success(
                request, 
                'Ürün talebiniz alındı! Ürününüz yönetici onayından sonra aktif hale gelecektir.'
            )
            return redirect('main:producer_dashboard')
        else:
            messages.error(request, 'Lütfen formdaki hataları düzeltin.')
    else:
        form = ProductForm(user=request.user)
    
    return render(request, 'user_area/add_product.html', {'form': form})


@login_required
def edit_product_view(request, product_id):
    """Edit product view (producers only)"""
    product = get_object_or_404(Product, id=product_id, producer=request.user)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ürün başarıyla güncellendi!')
            return redirect('main:producer_dashboard')
        else:
            messages.error(request, 'Lütfen formdaki hataları düzeltin.')
    else:
        form = ProductForm(instance=product, user=request.user)
    
    return render(request, 'user_area/edit_product.html', {'form': form, 'product': product})


@login_required
def delete_product_view(request, product_id):
    """Delete product view (producers only)"""
    product = get_object_or_404(Product, id=product_id, producer=request.user)
    
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Ürün başarıyla silindi!')
        return redirect('main:producer_dashboard')
    
    return render(request, 'user_area/delete_product.html', {'product': product})


@login_required
def product_detail_view(request, product_id):
    """Product detail view"""
    product = get_object_or_404(Product, id=product_id)
    
    # Check if user has permission to view this product
    # Producers can see their own products, buyers can see active products
    can_view = False
    if request.user == product.producer:
        can_view = True
    elif hasattr(request.user, 'profile') and request.user.profile.is_buyer and product.is_active:
        can_view = True
    
    if not can_view:
        messages.error(request, 'Bu ürünü görüntüleme yetkiniz yok.')
        return redirect('main:dashboard')
    
    # Fetch other products from the same seller in the same category
    other_products = Product.objects.filter(
        producer=product.producer,
        sector=product.sector,
        is_active=True
    ).exclude(id=product.id).order_by('-created_at')[:4]
    
    context = {
        'product': product,
        'is_owner': request.user == product.producer,
        'other_products': other_products,
    }
    
    return render(request, 'user_area/product_detail.html', context)


@login_required
def dashboard_calendar_view(request):
    """Dashboard calendar view - shows expos with signup functionality"""
    from django.utils import timezone
    
    # Get all active expos
    expos = Expo.objects.filter(is_active=True).order_by('start_date')
    
    # Separate upcoming and past expos
    today = timezone.now().date()
    upcoming_expos = expos.filter(start_date__gte=today)
    past_expos = expos.filter(start_date__lt=today)
    
    # Get user's signups
    user_signups = ExpoSignup.objects.filter(user=request.user).select_related('expo')
    user_signup_expo_ids = set(user_signups.values_list('expo_id', flat=True))
    confirmed_count = user_signups.filter(status='confirmed').count()
    
    context = {
        'upcoming_expos': upcoming_expos,
        'past_expos': past_expos,
        'user_signups': user_signups,
        'user_signup_expo_ids': user_signup_expo_ids,
        'confirmed_count': confirmed_count,
    }
    
    return render(request, 'user_area/dashboard_calendar.html', context)


@login_required
def expo_signup_view(request, expo_id):
    """Expo signup view - allows users to sign up for an expo"""
    from django.utils import timezone
    
    expo = get_object_or_404(Expo, id=expo_id, is_active=True)
    
    # Check if registration is still open
    if not expo.is_registration_open():
        messages.error(request, 'Bu fuar için kayıt süresi dolmuştur.')
        return redirect('main:dashboard_calendar')
    
    # Check if user already signed up
    existing_signup = ExpoSignup.objects.filter(expo=expo, user=request.user).first()
    if existing_signup:
        messages.warning(request, 'Bu fuara zaten kayıt oldunuz.')
        return redirect('main:dashboard_calendar')
    
    if request.method == 'POST':
        form = ExpoSignupForm(request.POST, user=request.user)
        if form.is_valid():
            signup = form.save(commit=False)
            signup.expo = expo
            signup.user = request.user
            signup.save()
            
            # If using listed products, add them to the many-to-many relationship
            if form.cleaned_data.get('uses_listed_products'):
                signup.selected_products.set(form.cleaned_data.get('selected_products'))
            
            messages.success(request, f'{expo.title_tr} fuarına başarıyla kayıt oldunuz!')
            return redirect('main:dashboard_calendar')
        else:
            messages.error(request, 'Lütfen formdaki hataları düzeltin.')
    else:
        form = ExpoSignupForm(user=request.user)
    
    context = {
        'expo': expo,
        'form': form,
    }
    
    return render(request, 'user_area/expo_signup.html', context)
