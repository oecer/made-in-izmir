from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'country', 'city', 'is_buyer', 'is_producer', 'created_at')
    list_filter = ('is_buyer', 'is_producer', 'country', 'created_at')
    search_fields = ('user__username', 'user__email', 'company_name', 'phone_number')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('buyer_interested_sectors', 'producer_sectors')
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Company Information', {
            'fields': ('company_name', 'phone_number', 'country', 'city')
        }),
        ('User Type', {
            'fields': ('is_buyer', 'is_producer')
        }),
        ('Buyer Information', {
            'fields': ('buyer_interested_sectors', 'buyer_quarterly_volume'),
            'classes': ('collapse',)
        }),
        ('Producer Information', {
            'fields': ('producer_sectors', 'producer_quarterly_sales', 'producer_product_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
