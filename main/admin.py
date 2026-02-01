from django.contrib import admin
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib import messages
from .models import UserProfile, SignupRequest, Sector, ProductTag, Product


@admin.register(SignupRequest)
class SignupRequestAdmin(admin.ModelAdmin):
    list_display = (
        'username', 'email', 'company_name', 'country', 
        'is_buyer', 'is_producer', 'status', 'created_at'
    )
    list_filter = ('status', 'is_buyer', 'is_producer', 'country', 'created_at')
    search_fields = ('username', 'email', 'company_name', 'phone_number', 'first_name', 'last_name')
    readonly_fields = (
        'created_at', 'updated_at', 'reviewed_by', 'reviewed_at', 'password_hash',
        'buyer_interested_sectors_display', 'producer_sectors_display'
    )
    
    fieldsets = (
        ('Request Status', {
            'fields': ('status', 'reviewed_by', 'reviewed_at', 'rejection_reason')
        }),
        ('User Account Information', {
            'fields': ('username', 'email', 'first_name', 'last_name', 'password_hash')
        }),
        ('Company Information', {
            'fields': ('company_name', 'phone_number', 'country', 'city')
        }),
        ('User Type', {
            'fields': ('is_buyer', 'is_producer')
        }),
        ('Buyer Information', {
            'fields': ('buyer_interested_sectors_ids', 'buyer_interested_sectors_display', 'buyer_quarterly_volume'),
        }),
        ('Producer Information', {
            'fields': ('producer_sectors_ids', 'producer_sectors_display', 'producer_quarterly_sales', 'producer_product_count'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )
    
    actions = ['approve_signups', 'reject_signups']
    
    def buyer_interested_sectors_display(self, obj):
        """Display buyer interested sectors"""
        sectors = obj.get_buyer_sectors()
        if sectors.exists():
            return ', '.join([f"{s.name_tr} | {s.name_en}" for s in sectors])
        return '-'
    buyer_interested_sectors_display.short_description = 'İlgilenilen Sektörler'
    
    def producer_sectors_display(self, obj):
        """Display producer sectors"""
        sectors = obj.get_producer_sectors()
        if sectors.exists():
            return ', '.join([f"{s.name_tr} | {s.name_en}" for s in sectors])
        return '-'
    producer_sectors_display.short_description = 'Sektörler'
    
    def get_readonly_fields(self, request, obj=None):
        """Make all fields readonly except status and rejection_reason for pending requests"""
        if obj and obj.status == 'pending':
            return ('created_at', 'updated_at', 'reviewed_by', 'reviewed_at', 'password_hash',
                    'username', 'email', 'first_name', 'last_name', 'company_name', 
                    'phone_number', 'country', 'city', 'is_buyer', 'is_producer',
                    'buyer_interested_sectors_ids', 'buyer_interested_sectors_display', 'buyer_quarterly_volume',
                    'producer_sectors_ids', 'producer_sectors_display', 'producer_quarterly_sales', 'producer_product_count')
        return ('created_at', 'updated_at', 'reviewed_by', 'reviewed_at', 'password_hash',
                'buyer_interested_sectors_display', 'producer_sectors_display',
                'username', 'email', 'first_name', 'last_name', 'company_name', 
                'phone_number', 'country', 'city', 'is_buyer', 'is_producer',
                'buyer_interested_sectors_ids', 'buyer_quarterly_volume',
                'producer_sectors_ids', 'producer_quarterly_sales', 'producer_product_count')
    
    def save_model(self, request, obj, form, change):
        """Handle status changes from the admin change form"""
        # If status is changing to approved, run approval logic
        if change and 'status' in form.changed_data and obj.status == 'approved':
            try:
                # Check previous status from DB
                old_instance = SignupRequest.objects.get(pk=obj.pk)
                if old_instance.status == 'pending':
                    self._process_approval(request, obj)
            except Exception as e:
                # Revert status if failed
                obj.status = 'pending'
                obj.reviewed_by = None
                obj.reviewed_at = None
                messages.error(request, f"Onay işlemi başarısız oldu: {str(e)}")
        
        super().save_model(request, obj, form, change)

    def _process_approval(self, request, signup_request):
        """Helper to create User and Profile - NO SAVE"""
        from django.db import transaction
        
        # Check uniqueness
        if User.objects.filter(username=signup_request.username).exists():
            raise ValueError(f"Username '{signup_request.username}' already exists")
        
        if User.objects.filter(email=signup_request.email).exists():
            raise ValueError(f"Email '{signup_request.email}' already exists")
            
        # Create user
        user = User.objects.create(
            username=signup_request.username,
            email=signup_request.email,
            first_name=signup_request.first_name,
            last_name=signup_request.last_name,
            password=signup_request.password_hash
        )
        
        # Create user profile
        profile = UserProfile.objects.create(
            user=user,
            company_name=signup_request.company_name,
            phone_number=signup_request.phone_number,
            country=signup_request.country,
            city=signup_request.city,
            is_buyer=signup_request.is_buyer,
            is_producer=signup_request.is_producer,
            buyer_quarterly_volume=signup_request.buyer_quarterly_volume,
            producer_quarterly_sales=signup_request.producer_quarterly_sales,
            producer_product_count=signup_request.producer_product_count
        )
        
        # Add sectors
        if signup_request.buyer_interested_sectors_ids:
            buyer_sectors = signup_request.get_buyer_sectors()
            if buyer_sectors.exists():
                profile.buyer_interested_sectors.set(buyer_sectors)
        
        if signup_request.producer_sectors_ids:
            producer_sectors = signup_request.get_producer_sectors()
            if producer_sectors.exists():
                profile.producer_sectors.set(producer_sectors)
        
        # Update request fields
        signup_request.reviewed_by = request.user
        signup_request.reviewed_at = timezone.now()

    def approve_signups(self, request, queryset):
        """Approve selected signup requests and create user accounts"""
        from django.db import transaction
        
        approved_count = 0
        error_count = 0
        
        for signup_request in queryset.filter(status='pending'):
            try:
                with transaction.atomic():
                    self._process_approval(request, signup_request)
                    signup_request.status = 'approved'
                    signup_request.save()
                    approved_count += 1
                    
            except Exception as e:
                error_count += 1
                messages.error(request, f"Error ({signup_request.username}): {str(e)}")
        
        if approved_count > 0:
            messages.success(request, f"✓ {approved_count} signup request(s) approved successfully!")
        if error_count > 0:
            messages.warning(request, f"⚠ {error_count} request(s) failed.")

    approve_signups.short_description = "Approve selected signup requests"
    
    def reject_signups(self, request, queryset):
        """Reject selected signup requests"""
        rejected_count = queryset.filter(status='pending').update(
            status='rejected',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        
        if rejected_count > 0:
            messages.success(request, f"{rejected_count} signup request(s) rejected.")
    
    reject_signups.short_description = "Reject selected signup requests"


@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ('name_tr', 'name_en')
    search_fields = ('name_tr', 'name_en')


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


@admin.register(ProductTag)
class ProductTagAdmin(admin.ModelAdmin):
    list_display = ('name_tr', 'name_en')
    search_fields = ('name_tr', 'name_en')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title_tr', 'title_en', 'producer', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at', 'tags')
    search_fields = ('title_tr', 'title_en', 'description_tr', 'description_en', 'producer__username')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('tags',)
    
    fieldsets = (
        ('Producer', {
            'fields': ('producer',)
        }),
        ('Product Information (Turkish)', {
            'fields': ('title_tr', 'description_tr')
        }),
        ('Product Information (English)', {
            'fields': ('title_en', 'description_en')
        }),
        ('Photos', {
            'fields': ('photo1', 'photo2', 'photo3')
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
        """Limit products to those created by producers"""
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            # If user is not superuser, only show their products
            return qs.filter(producer=request.user)
        return qs
