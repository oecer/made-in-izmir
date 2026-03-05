from django.contrib import admin
from django.utils.html import format_html
from .models import Expo, ExpoSignup


@admin.register(Expo)
class ExpoAdmin(admin.ModelAdmin):
    list_display = ('title_tr', 'title_en', 'location_tr', 'start_date', 'end_date', 'registration_deadline', 'is_active', 'created_at')
    list_filter = ('is_active', 'start_date', 'created_at')
    search_fields = ('title_tr', 'title_en', 'description_tr', 'description_en', 'location_tr', 'location_en')
    readonly_fields = ('created_at', 'updated_at', 'image_preview')

    fieldsets = (
        ('Expo Information (Turkish)', {
            'fields': ('title_tr', 'description_tr', 'location_tr')
        }),
        ('Expo Information (English)', {
            'fields': ('title_en', 'description_en', 'location_en')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date', 'registration_deadline')
        }),
        ('Image', {
            'fields': ('image', 'image_preview')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width: 300px; max-height: 300px;" />', obj.image.url)
        return '-'
    image_preview.short_description = 'Görsel Önizleme'


@admin.register(ExpoSignup)
class ExpoSignupAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_user_company', 'expo', 'product_count', 'uses_listed_products', 'status', 'created_at')
    list_filter = ('status', 'uses_listed_products', 'expo', 'created_at')
    search_fields = ('user__username', 'user__email', 'tenant__company_name', 'expo__title_tr', 'expo__title_en')
    readonly_fields = ('created_at', 'updated_at', 'selected_products_display')
    filter_horizontal = ('selected_products',)

    fieldsets = (
        ('Expo & User', {
            'fields': ('expo', 'user')
        }),
        ('Product Information', {
            'fields': ('product_count', 'uses_listed_products', 'selected_products', 'selected_products_display', 'product_description')
        }),
        ('Additional Information', {
            'fields': ('notes', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_user_company(self, obj):
        if obj.tenant:
            return obj.tenant.company_name
        if hasattr(obj.user, 'profile') and obj.user.profile.tenant:
            return obj.user.profile.tenant.company_name
        return '-'
    get_user_company.short_description = 'Firma'

    def selected_products_display(self, obj):
        products = obj.selected_products.all()
        if products.exists():
            return ', '.join([p.title_tr or p.title_en for p in products])
        return '-'
    selected_products_display.short_description = 'Seçilen Ürünler'
