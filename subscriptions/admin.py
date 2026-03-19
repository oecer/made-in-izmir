from django.contrib import admin
from django.utils.html import format_html, mark_safe
from .models import SubscriptionPlan, TenantSubscription


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = (
        'name_tr', 'monthly_price', 'show_company_profile',
        'display_company_name', 'display_city', 'has_business_card',
        'max_active_products_display', 'display_order', 'is_active',
        'subscriber_count',
    )
    list_editable = ('display_order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name_tr', 'name_en')

    fieldsets = (
        ('Plan Kimliği', {
            'fields': ('name_tr', 'name_en', 'description_tr', 'description_en',
                       'monthly_price', 'display_order', 'is_active')
        }),
        ('Erişim Özellikleri', {
            'fields': (
                'show_company_profile',
                'company_username_editable',
                'has_business_card',
                'display_company_name',
                'display_open_address',
                'display_city',
                'display_phone',
                'display_email',
                'display_website',
            ),
            'description': 'Bu özellikler bu plana sahip firmaların erişebileceği işlevleri belirler.',
        }),
        ('Limitler', {
            'fields': ('max_active_products',),
            'description': 'Boş bırakılırsa sınırsız.'
        }),
    )

    def max_active_products_display(self, obj):
        if obj.max_active_products is None:
            return mark_safe('<span style="color:green;">Sınırsız</span>')
        return obj.max_active_products
    max_active_products_display.short_description = 'Maks. Aktif Ürün'

    def subscriber_count(self, obj):
        return obj.subscriptions.filter(status='active').count()
    subscriber_count.short_description = 'Aktif Abone'


@admin.register(TenantSubscription)
class TenantSubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'tenant', 'plan', 'status', 'started_at', 'expires_at',
        'assigned_by', 'is_active_badge',
    )
    list_filter = ('status', 'plan', 'started_at')
    search_fields = ('tenant__company_name', 'tenant__company_username')
    raw_id_fields = ('tenant',)
    readonly_fields = ('assigned_by', 'created_at', 'updated_at')
    date_hierarchy = 'started_at'

    fieldsets = (
        ('Firma', {
            'fields': ('tenant',)
        }),
        ('Plan & Durum', {
            'fields': ('plan', 'status', 'started_at', 'expires_at')
        }),
        ('Admin Notları', {
            'fields': ('notes',)
        }),
        ('Sistem Bilgisi', {
            'fields': ('assigned_by', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.assigned_by_id:
            obj.assigned_by = request.user
        super().save_model(request, obj, form, change)

    def is_active_badge(self, obj):
        if obj.is_currently_active():
            return mark_safe('<span style="color:green;font-weight:bold;">✓ Aktif</span>')
        return mark_safe('<span style="color:red;">✗ Pasif</span>')
    is_active_badge.short_description = 'Aktif mi?'
