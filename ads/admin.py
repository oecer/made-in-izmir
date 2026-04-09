from django.contrib import admin
from django.utils.html import format_html

from .models import Ad, AdSlot


@admin.register(AdSlot)
class AdSlotAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'slug', 'dimensions_display', 'ad_type',
        'is_active', 'grid_interval', 'price_daily', 'price_monthly', 'price_currency',
    )
    list_filter = ('ad_type', 'is_active')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('name', 'slug', 'description', 'ad_type', 'is_active'),
        }),
        ('Boyutlar', {
            'fields': ('width_px', 'height_px'),
            'description': 'Reklamın piksel cinsinden boyutları. CSS placeholder ve görsel için kullanılır.',
        }),
        ('Grid Ayarları', {
            'fields': ('grid_interval', 'max_ads_in_grid'),
            'description': 'Yalnızca <strong>grid_card</strong> tipindeki slotlar için geçerlidir.',
            'classes': ('collapse',),
        }),
        ('Fiyatlandırma', {
            'fields': ('price_daily', 'price_weekly', 'price_monthly', 'price_currency'),
            'description': 'Bu slot için reklamveren fiyatları. Boş bırakılabilir.',
        }),
    )

    def dimensions_display(self, obj):
        return f'{obj.width_px} × {obj.height_px} px'
    dimensions_display.short_description = 'Boyutlar'


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = (
        'advertiser_name', 'slot', 'start_date', 'end_date',
        'order', 'is_active', 'currently_active_display', 'image_preview',
    )
    list_filter = ('slot', 'is_active', 'start_date', 'end_date')
    search_fields = ('advertiser_name', 'title')
    ordering = ('slot', 'order')
    date_hierarchy = 'start_date'

    fieldsets = (
        ('Reklam Bilgileri', {
            'fields': ('slot', 'advertiser_name', 'title', 'link_url'),
        }),
        ('Görsel', {
            'fields': ('image',),
            'description': 'Görsel yüklenmezse CSS placeholder gösterilir.',
        }),
        ('Yayın Dönemi', {
            'fields': ('start_date', 'end_date'),
        }),
        ('Yayın Ayarları', {
            'fields': ('order', 'is_active', 'display_duration_seconds'),
            'description': '<strong>Sıralama</strong>: Küçük değer önce gösterilir. '
                           '<strong>Gösterim Süresi</strong>: Aynı slotta birden fazla reklam varsa '
                           'bu reklam kaç saniye gösterileceğini belirler.',
        }),
        ('Sistem Bilgileri', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width:120px;max-height:40px;'
                'object-fit:contain;border-radius:4px;border:1px solid #eee;">',
                obj.image.url,
            )
        return '<span style="color:#aaa;font-style:italic;">CSS placeholder</span>'
    image_preview.short_description = 'Önizleme'

    def currently_active_display(self, obj):
        if obj.is_currently_active:
            return format_html('<span style="color:{};font-weight:600;">✓ Yayında</span>', '#16a34a')
        return format_html('<span style="color:{};">✗ Yayında değil</span>', '#dc2626')
    currently_active_display.short_description = 'Durum'
