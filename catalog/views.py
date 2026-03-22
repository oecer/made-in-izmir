from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProductForm
from .models import Product, ProductTag, ProductRequest, Sector


@login_required
def producer_dashboard_view(request):
    """Producer dashboard view"""
    try:
        profile = request.user.profile
        tenant = profile.tenant
        if not tenant or not tenant.is_producer:
            messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
            return redirect('accounts:dashboard')

        status_filters = request.GET.getlist('status')
        tag_filters = [t for t in request.GET.getlist('tag') if t]
        sector_filters = [s for s in request.GET.getlist('sector') if s]
        search_query = request.GET.get('search', '').strip()

        products_qs = Product.objects.filter(tenant=tenant)
        requests_qs = ProductRequest.objects.filter(tenant=tenant, status='pending')

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

        if sector_filters:
            products_qs = products_qs.filter(sector_id__in=sector_filters)
            requests_qs = requests_qs.filter(sector_id__in=sector_filters)

        if tag_filters:
            products_qs = products_qs.filter(tags__id__in=tag_filters).distinct()
            selected_tag_set = set(str(t) for t in tag_filters)
            request_list = []
            for r in requests_qs:
                r_tags = (r.tags_ids or '').split(',')
                if any(t.strip() in selected_tag_set for t in r_tags if t.strip()):
                    request_list.append(r)
        else:
            request_list = list(requests_qs)

        display_items = list(products_qs)
        for req in request_list:
            req.is_pending = True
            display_items.append(req)

        display_items.sort(key=lambda x: x.created_at, reverse=True)

        unfiltered_products = Product.objects.filter(tenant=tenant)
        pending_count = ProductRequest.objects.filter(tenant=tenant, status='pending').count()

        active_count = unfiltered_products.filter(is_active=True).count()
        active_plan = tenant.get_active_plan()

        context = {
            'profile': profile,
            'products': display_items,
            'total_products': unfiltered_products.count() + pending_count,
            'active_products': active_count,
            'pending_products_count': pending_count,
            'available_tags': available_tags,
            'available_sectors': available_sectors,
            'current_filters': {
                'status': status_filters,
                'tag': tag_filters,
                'sector': sector_filters,
            },
            'search_query': search_query,
            'active_product_count': active_count,
            'max_active_products': active_plan.max_active_products if active_plan else None,
            'can_add_product': tenant.can_activate_product(),
        }

        return render(request, 'user_area/producer_dashboard.html', context)
    except Exception as e:
        messages.error(request, f'Sistem hatası: {str(e)}')
        return redirect('accounts:dashboard')


@login_required
def buyer_dashboard_view(request):
    """Buyer dashboard view"""
    try:
        profile = request.user.profile
        tenant = profile.tenant
        if not tenant or not tenant.is_buyer:
            messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
            return redirect('accounts:dashboard')

        try:
            tag_filters = [int(t) for t in request.GET.getlist('tag') if t]
            sector_filters = [int(s) for s in request.GET.getlist('sector') if s]
            producer_filters = [int(p) for p in request.GET.getlist('producer') if p]
        except ValueError:
            tag_filters = sector_filters = producer_filters = []
        search_query = request.GET.get('search', '').strip()

        products_qs = Product.objects.filter(is_active=True)

        if search_query:
            from django.db.models import Q
            products_qs = products_qs.filter(
                Q(title_tr__icontains=search_query) |
                Q(title_en__icontains=search_query) |
                Q(description_tr__icontains=search_query) |
                Q(description_en__icontains=search_query)
            )

        if sector_filters:
            products_qs = products_qs.filter(sector_id__in=sector_filters)

        if tag_filters:
            products_qs = products_qs.filter(tags__id__in=tag_filters).distinct()

        if producer_filters:
            products_qs = products_qs.filter(producer_id__in=producer_filters)

        products_qs = products_qs.order_by('-created_at')

        all_active_products = Product.objects.filter(is_active=True)

        available_tag_ids = all_active_products.values_list('tags', flat=True).distinct()
        available_tags = ProductTag.objects.filter(id__in=available_tag_ids).distinct()

        available_sector_ids = all_active_products.values_list('sector_id', flat=True).distinct()
        available_sectors = Sector.objects.filter(id__in=available_sector_ids).distinct()

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
    except Exception:
        messages.error(request, 'Profil bilgileriniz bulunamadı.')
        return redirect('main:index')


@login_required
def add_product_view(request):
    """Add new product view (producers only) - creates product request for admin approval"""
    try:
        profile = request.user.profile
        tenant = profile.tenant
        if not tenant or not tenant.is_producer:
            messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
            return redirect('accounts:dashboard')
        if profile.tenant_role == 'read_only':
            messages.error(request, 'Salt okunur kullanıcılar ürün ekleyemez.')
            return redirect('accounts:dashboard')
        if not tenant.can_activate_product():
            plan = tenant.get_active_plan()
            limit = plan.max_active_products if plan else '?'
            messages.error(
                request,
                f'Aktif ürün limitinize ({limit} ürün) ulaştınız. '
                f'Daha fazla ürün eklemek için aboneliğinizi yükseltin.'
            )
            return redirect('catalog:producer_dashboard')
    except Exception:
        messages.error(request, 'Profil bilgileriniz bulunamadı.')
        return redirect('main:index')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            tags = form.cleaned_data.get('tags', [])
            tag_ids = ','.join(str(tag.id) for tag in tags) if tags else ''

            ProductRequest.objects.create(
                producer=request.user,
                tenant=tenant,
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
            return redirect('catalog:producer_dashboard')
        else:
            messages.error(request, 'Lütfen formdaki hataları düzeltin.')
    else:
        form = ProductForm(user=request.user)

    return render(request, 'user_area/add_product.html', {'form': form})


@login_required
def edit_product_view(request, product_id):
    """Edit product view (producers only) - any tenant member can edit"""
    profile = request.user.profile
    product = get_object_or_404(Product, id=product_id, tenant=profile.tenant)

    if profile.tenant_role == 'read_only':
        messages.error(request, 'Salt okunur kullanıcılar ürün düzenleyemez.')
        return redirect('catalog:producer_dashboard')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ürün başarıyla güncellendi!')
            return redirect('catalog:producer_dashboard')
        else:
            messages.error(request, 'Lütfen formdaki hataları düzeltin.')
    else:
        form = ProductForm(instance=product, user=request.user)

    return render(request, 'user_area/edit_product.html', {'form': form, 'product': product})


@login_required
def delete_product_view(request, product_id):
    """Delete product view (producers only) - any tenant member can delete"""
    profile = request.user.profile
    product = get_object_or_404(Product, id=product_id, tenant=profile.tenant)

    if profile.tenant_role == 'read_only':
        messages.error(request, 'Salt okunur kullanıcılar ürün silemez.')
        return redirect('catalog:producer_dashboard')

    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Ürün başarıyla silindi!')
        return redirect('catalog:producer_dashboard')

    return render(request, 'user_area/delete_product.html', {'product': product})


@login_required
def product_detail_view(request, product_id):
    """Product detail view"""
    user_tenant = getattr(getattr(request.user, 'profile', None), 'tenant', None)

    if user_tenant and user_tenant.is_buyer:
        product = get_object_or_404(Product, id=product_id, is_active=True)
    elif user_tenant:
        product = get_object_or_404(Product, id=product_id, tenant=user_tenant)
    else:
        messages.error(request, 'Bu ürünü görüntüleme yetkiniz yok.')
        return redirect('accounts:dashboard')

    other_products = Product.objects.filter(
        tenant=product.tenant,
        sector=product.sector,
        is_active=True
    ).exclude(id=product.id).order_by('-created_at')[:4]

    context = {
        'product': product,
        'is_owner': user_tenant == product.tenant,
        'other_products': other_products,
        'producer_plan': product.tenant.get_active_plan() if product.tenant else None,
    }

    return render(request, 'user_area/product_detail.html', context)
