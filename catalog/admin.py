from django.contrib import admin
from django.utils import timezone
from django.contrib import messages
from django.utils.html import format_html
from .models import Sector, ProductTag, ProductRequest, Product


def _photo_preview(field):
    """Render a photo field as an inline image, or '-' if missing/unavailable."""
    if not field:
        return '-'
    try:
        url = field.url
    except ValueError:
        return '-'
    return format_html(
        '<a href="{url}" target="_blank">'
        '<img src="{url}" style="max-width:300px; max-height:300px; object-fit:contain; border:1px solid #ddd; border-radius:4px; padding:4px;" />'
        '</a>',
        url=url,
    )


@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ('name_tr', 'name_en')
    search_fields = ('name_tr', 'name_en')


@admin.register(ProductTag)
class ProductTagAdmin(admin.ModelAdmin):
    list_display = ('name_tr', 'name_en')
    search_fields = ('name_tr', 'name_en')


@admin.register(ProductRequest)
class ProductRequestAdmin(admin.ModelAdmin):
    list_display = (
        'get_title', 'producer', 'get_producer_company', 'status', 'created_at'
    )
    list_filter = ('status', 'created_at', 'is_active')
    search_fields = ('title_tr', 'title_en', 'description_tr', 'description_en', 'producer__username', 'tenant__company_name')
    readonly_fields = (
        'created_at', 'updated_at', 'reviewed_by', 'reviewed_at', 'tags_display',
        'photo1_preview', 'photo2_preview', 'photo3_preview'
    )

    fieldsets = (
        ('Request Status', {
            'fields': ('status', 'reviewed_by', 'reviewed_at', 'rejection_reason')
        }),
        ('Producer', {
            'fields': ('producer',)
        }),
        ('Sector', {
            'fields': ('sector',)
        }),
        ('Product Information (Turkish)', {
            'fields': ('title_tr', 'description_tr')
        }),
        ('Product Information (English)', {
            'fields': ('title_en', 'description_en')
        }),
        ('Photos', {
            'fields': ('photo1', 'photo1_preview', 'photo2', 'photo2_preview', 'photo3', 'photo3_preview')
        }),
        ('Tags & Status', {
            'fields': ('tags_ids', 'tags_display', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    actions = ['approve_products', 'reject_products']

    def get_title(self, obj):
        return obj.title_tr or obj.title_en or f"Product Request #{obj.id}"
    get_title.short_description = 'Ürün'

    def get_producer_company(self, obj):
        if hasattr(obj.producer, 'profile') and obj.producer.profile.tenant:
            return obj.producer.profile.tenant.company_name
        return '-'
    get_producer_company.short_description = 'Firma'

    def tags_display(self, obj):
        tags = obj.get_tags()
        if tags.exists():
            return ', '.join([f"{t.name_tr} | {t.name_en}" for t in tags])
        return '-'
    tags_display.short_description = 'Etiketler'

    def photo1_preview(self, obj):
        return _photo_preview(obj.photo1)
    photo1_preview.short_description = 'Fotoğraf 1 Önizleme'

    def photo2_preview(self, obj):
        return _photo_preview(obj.photo2)
    photo2_preview.short_description = 'Fotoğraf 2 Önizleme'

    def photo3_preview(self, obj):
        return _photo_preview(obj.photo3)
    photo3_preview.short_description = 'Fotoğraf 3 Önizleme'

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status == 'pending':
            return ('created_at', 'updated_at', 'reviewed_by', 'reviewed_at', 'tags_display',
                    'photo1_preview', 'photo2_preview', 'photo3_preview',
                    'producer', 'sector', 'title_tr', 'title_en', 'description_tr', 'description_en',
                    'photo1', 'photo2', 'photo3', 'tags_ids', 'is_active')
        return ('created_at', 'updated_at', 'reviewed_by', 'reviewed_at', 'tags_display',
                'photo1_preview', 'photo2_preview', 'photo3_preview',
                'producer', 'sector', 'title_tr', 'title_en', 'description_tr', 'description_en',
                'photo1', 'photo2', 'photo3', 'tags_ids', 'is_active')

    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data and obj.status == 'approved':
            try:
                old_instance = ProductRequest.objects.get(pk=obj.pk)
                if old_instance.status == 'pending':
                    self._process_approval(request, obj)
            except Exception as e:
                obj.status = 'pending'
                obj.reviewed_by = None
                obj.reviewed_at = None
                messages.error(request, f"Onay işlemi başarısız oldu: {str(e)}")

        super().save_model(request, obj, form, change)

    def _process_approval(self, request, product_request):
        # Enforce subscription product limit if the approved product will be active
        if product_request.is_active and product_request.tenant:
            if not product_request.tenant.can_activate_product():
                plan = product_request.tenant.get_active_plan()
                limit = plan.max_active_products if plan else '?'
                raise ValueError(
                    f"'{product_request.tenant.company_name}' firması aktif ürün limitine "
                    f"ulaştı ({limit} ürün). Abonelik yükseltilmeden ürün onaylanamaz."
                )

        # Create product without photos first to get a PK
        product = Product.objects.create(
            producer=product_request.producer,
            tenant=product_request.tenant,
            sector=product_request.sector,
            title_tr=product_request.title_tr,
            title_en=product_request.title_en,
            description_tr=product_request.description_tr,
            description_en=product_request.description_en,
            is_active=product_request.is_active
        )
        # Set photo paths via QuerySet.update() — this writes the path string directly
        # to the DB column without passing through the storage backend's save(), which
        # would otherwise copy the file or generate a unique suffix.
        photo_update = {
            field: getattr(product_request, field).name
            for field in ('photo1', 'photo2', 'photo3')
            if getattr(product_request, field)
        }
        if photo_update:
            Product.objects.filter(pk=product.pk).update(**photo_update)
            product.refresh_from_db()

        if product_request.tags_ids:
            tags = product_request.get_tags()
            if tags.exists():
                product.tags.set(tags)

        product_request.reviewed_by = request.user
        product_request.reviewed_at = timezone.now()
        # Clear photo references on the request so the shared files aren't
        # accidentally deleted if the ProductRequest record is cleaned up later.
        product_request.photo1 = None
        product_request.photo2 = None
        product_request.photo3 = None

    def approve_products(self, request, queryset):
        from django.db import transaction

        approved_count = 0
        error_count = 0

        for product_request in queryset.filter(status='pending'):
            try:
                with transaction.atomic():
                    self._process_approval(request, product_request)
                    product_request.status = 'approved'
                    product_request.save()
                    approved_count += 1
            except Exception as e:
                error_count += 1
                messages.error(request, f"Error: {str(e)}")

        if approved_count > 0:
            messages.success(request, f"✓ {approved_count} product request(s) approved successfully!")
        if error_count > 0:
            messages.warning(request, f"⚠ {error_count} request(s) failed.")

    approve_products.short_description = "Approve selected product requests"

    def reject_products(self, request, queryset):
        pending = queryset.filter(status='pending')
        rejected_count = 0

        for pr in pending:
            # Delete photo files from disk — they're no longer needed
            for field in [pr.photo1, pr.photo2, pr.photo3]:
                if field:
                    field.delete(save=False)
            pr.status = 'rejected'
            pr.reviewed_by = request.user
            pr.reviewed_at = timezone.now()
            pr.photo1 = None
            pr.photo2 = None
            pr.photo3 = None
            pr.save()
            rejected_count += 1

        if rejected_count > 0:
            messages.success(request, f"{rejected_count} product request(s) rejected and photos cleaned up.")

    reject_products.short_description = "Reject selected product requests"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title_tr', 'title_en', 'producer', 'sector', 'is_active', 'created_at')
    list_filter = ('is_active', 'sector', 'created_at', 'tags')
    search_fields = ('title_tr', 'title_en', 'description_tr', 'description_en', 'producer__username')
    readonly_fields = ('created_at', 'updated_at', 'photo1_preview', 'photo2_preview', 'photo3_preview')
    filter_horizontal = ('tags',)

    def photo1_preview(self, obj):
        if obj.photo1:
            return format_html('<img src="{}" style="max-width: 200px; max-height: 200px;" />', obj.photo1.url)
        return '-'
    photo1_preview.short_description = 'Fotoğraf 1 Önizleme'

    def photo2_preview(self, obj):
        return _photo_preview(obj.photo2)
    photo2_preview.short_description = 'Fotoğraf 2 Önizleme'

    def photo3_preview(self, obj):
        return _photo_preview(obj.photo3)
    photo3_preview.short_description = 'Fotoğraf 3 Önizleme'

    fieldsets = (
        ('Producer', {
            'fields': ('producer',)
        }),
        ('Sector', {
            'fields': ('sector',)
        }),
        ('Product Information (Turkish)', {
            'fields': ('title_tr', 'description_tr')
        }),
        ('Product Information (English)', {
            'fields': ('title_en', 'description_en')
        }),
        ('Photos', {
            'fields': ('photo1', 'photo1_preview', 'photo2', 'photo2_preview', 'photo3', 'photo3_preview')
        }),
        ('Tags & Status', {
            'fields': ('tags', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(producer=request.user)
        return qs
