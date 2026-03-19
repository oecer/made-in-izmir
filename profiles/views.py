from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from accounts.models import Tenant, TenantPhotoRequest
from .forms import TenantLogoRequestForm, TenantPhotoRequestForm


def company_profile_view(request, company_username):
    """Public company profile/showroom page."""
    from django.shortcuts import get_object_or_404
    from django.http import Http404
    from catalog.models import Product

    tenant = get_object_or_404(Tenant, company_username=company_username)

    # Company profiles are only for producer tenants
    if not tenant.is_producer:
        raise Http404("Bu firma profili mevcut değil.")

    # Check if the visitor is the tenant admin (producer previewing their own profile)
    visitor_is_producer = False
    if request.user.is_authenticated:
        try:
            visitor_tenant = request.user.profile.tenant
            if visitor_tenant and visitor_tenant == tenant and visitor_tenant.is_producer:
                visitor_is_producer = True
        except Exception:
            pass

    if not tenant.show_company_profile and not visitor_is_producer:
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

    # Base showroom products for this tenant
    base_products = Product.objects.filter(tenant=tenant, is_active=True, in_showroom=True)

    # Collect available sectors and tags from this tenant's showroom products
    from catalog.models import Sector, ProductTag
    available_sectors = Sector.objects.filter(products__in=base_products).distinct().order_by('name_tr')
    available_tags = ProductTag.objects.filter(products__in=base_products).distinct().order_by('name_tr')

    # Apply filters from query string
    selected_sector_ids = request.GET.getlist('sector')
    selected_tag_ids = request.GET.getlist('tag')

    products = base_products
    if selected_sector_ids:
        try:
            selected_sector_ids = [int(i) for i in selected_sector_ids]
            products = products.filter(sector__id__in=selected_sector_ids)
        except (ValueError, TypeError):
            selected_sector_ids = []
    if selected_tag_ids:
        try:
            selected_tag_ids = [int(i) for i in selected_tag_ids]
            products = products.filter(tags__id__in=selected_tag_ids)
        except (ValueError, TypeError):
            selected_tag_ids = []

    products = products.distinct().order_by('-created_at')

    is_preview_for_producer = visitor_is_producer and not tenant.show_company_profile

    is_madeinizmir_user = False
    if request.user.is_authenticated:
        try:
            _ = request.user.profile
            is_madeinizmir_user = True
        except Exception:
            pass

    context = {
        'tenant': tenant,
        'gallery_photos': gallery_photos,
        'products': products,
        'is_tenant_admin': is_tenant_admin,
        'has_pending_logo': has_pending_logo,
        'pending_photo_count': pending_photo_count,
        'is_preview_for_producer': is_preview_for_producer,
        'is_madeinizmir_user': is_madeinizmir_user,
        'available_sectors': available_sectors,
        'available_tags': available_tags,
        'selected_sector_ids': selected_sector_ids,
        'selected_tag_ids': selected_tag_ids,
    }
    return render(request, 'company_profile/company_profile.html', context)


def business_card_view(request, company_username):
    """Printable bilingual business card for a producer or buyer."""
    from django.shortcuts import get_object_or_404
    from django.http import Http404

    tenant = get_object_or_404(Tenant, company_username=company_username)

    if not tenant.is_producer and not tenant.is_buyer:
        raise Http404("Bu firma profili mevcut değil.")

    context = {'tenant': tenant}
    return render(request, 'company_profile/business_card.html', context)


def submit_enquiry_view(request):
    """Handles producer enquiry form submissions from company profile and product detail pages."""
    from django.http import JsonResponse
    from accounts.models import Tenant, ProducerEnquiry
    from django.core.mail import send_mail
    from django.conf import settings

    if request.method != 'POST':
        return JsonResponse({'error': 'Geçersiz istek.'}, status=405)

    # Identify the producer from schema_name
    producer_schema = request.POST.get('producer', '').strip()
    if not producer_schema:
        return JsonResponse({'error': 'Üretici belirtilmedi.'}, status=400)

    try:
        producer = Tenant.objects.get(schema_name=producer_schema, is_producer=True)
    except Tenant.DoesNotExist:
        return JsonResponse({'error': 'Üretici bulunamadı.'}, status=404)

    name    = request.POST.get('name', '').strip()
    company = request.POST.get('company', '').strip()
    email   = request.POST.get('email', '').strip()
    phone   = request.POST.get('phone', '').strip()
    message = request.POST.get('message', '').strip()

    if not name or not email or not message:
        return JsonResponse({'error': 'Lütfen zorunlu alanları doldurun.'}, status=400)

    # Optional product context
    product_id    = request.POST.get('product_id', '').strip()
    product_title = request.POST.get('product_title', '').strip()

    # IP
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')

    # Build email body
    product_line = ''
    if product_title:
        product_line = f"Ürün:     {product_title}\n"
    if product_id:
        product_line += f"Ürün ID:  {product_id}\n"

    subject_line = f"[Made in İzmir] Sorgu: {producer.company_name} — {name}"
    body = (
        f"Üretici:  {producer.company_name}\n"
        f"{product_line}"
        f"Ad Soyad: {name}\n"
        f"Firma:    {company or '-'}\n"
        f"E-posta:  {email}\n"
        f"Telefon:  {phone or '-'}\n\n"
        f"Mesaj:\n{message}"
    )

    email_ok = True
    try:
        send_mail(
            subject_line,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [settings.DEFAULT_FROM_EMAIL],
            fail_silently=False,
        )
    except Exception:
        email_ok = False

    ProducerEnquiry.objects.create(
        producer=producer,
        product_id=int(product_id) if product_id and product_id.isdigit() else None,
        product_title=product_title,
        name=name,
        company=company,
        email=email,
        phone=phone,
        message=message,
        ip_address=ip,
        email_sent=email_ok,
    )

    if not email_ok:
        return JsonResponse({'error': 'E-posta gönderilemedi.'}, status=500)

    return JsonResponse({'success': True})


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

    if not tenant.is_producer:
        return JsonResponse({'error': 'Yalnızca üretici firmalar logo yükleyebilir.'}, status=403)

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

    if not tenant.is_producer:
        return JsonResponse({'error': 'Yalnızca üretici firmalar fotoğraf yükleyebilir.'}, status=403)

    has_pending_request = TenantPhotoRequest.objects.filter(tenant=tenant, status='pending').exists()
    if has_pending_request:
        return JsonResponse({'error': 'Zaten onay bekleyen bir fotoğraf talebiniz var.'}, status=400)

    form = TenantPhotoRequestForm(request.POST, request.FILES)
    if form.is_valid():
        photo_request = form.save(commit=False)
        photo_request.tenant = tenant
        photo_request.submitted_by = request.user
        photo_request.status = 'pending'
        photo_request.save()
        return JsonResponse({'success': True, 'message': 'Fotoğrafınız yönetici onayına gönderildi.'})

    return JsonResponse({'error': str(form.errors)}, status=400)
