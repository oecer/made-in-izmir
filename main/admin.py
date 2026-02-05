from django.contrib import admin
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib import messages
from .models import UserProfile, SignupRequest, Sector, ProductTag, Product, ProductRequest, Expo, ExpoSignup, ProfileEditRequest


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


@admin.register(ProfileEditRequest)
class ProfileEditRequestAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'get_user_company', 'get_user_email', 'status', 'created_at'
    )
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'user__email', 'company_name', 'phone_number', 'first_name', 'last_name')
    readonly_fields = (
        'created_at', 'updated_at', 'reviewed_by', 'reviewed_at',
        'buyer_interested_sectors_display', 'producer_sectors_display'
    )
    
    fieldsets = (
        ('Request Status', {
            'fields': ('status', 'reviewed_by', 'reviewed_at', 'rejection_reason')
        }),
        ('User', {
            'fields': ('user',)
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name')
        }),
        ('Company Information', {
            'fields': ('company_name', 'phone_number', 'country', 'city')
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
    
    actions = ['approve_profile_edits', 'reject_profile_edits']
    
    def get_user_company(self, obj):
        """Display user's current company name"""
        if hasattr(obj.user, 'profile'):
            return obj.user.profile.company_name
        return '-'
    get_user_company.short_description = 'Mevcut Firma'
    
    def get_user_email(self, obj):
        """Display user's email"""
        return obj.user.email
    get_user_email.short_description = 'E-posta'
    
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
            return ('created_at', 'updated_at', 'reviewed_by', 'reviewed_at',
                    'user', 'first_name', 'last_name', 'company_name', 
                    'phone_number', 'country', 'city',
                    'buyer_interested_sectors_ids', 'buyer_interested_sectors_display', 'buyer_quarterly_volume',
                    'producer_sectors_ids', 'producer_sectors_display', 'producer_quarterly_sales', 'producer_product_count')
        return ('created_at', 'updated_at', 'reviewed_by', 'reviewed_at',
                'buyer_interested_sectors_display', 'producer_sectors_display',
                'user', 'first_name', 'last_name', 'company_name', 
                'phone_number', 'country', 'city',
                'buyer_interested_sectors_ids', 'buyer_quarterly_volume',
                'producer_sectors_ids', 'producer_quarterly_sales', 'producer_product_count')
    
    def save_model(self, request, obj, form, change):
        """Handle status changes from the admin change form"""
        if change and 'status' in form.changed_data and obj.status == 'approved':
            try:
                old_instance = ProfileEditRequest.objects.get(pk=obj.pk)
                if old_instance.status == 'pending':
                    self._process_approval(request, obj)
            except Exception as e:
                obj.status = 'pending'
                obj.reviewed_by = None
                obj.reviewed_at = None
                messages.error(request, f"Onay işlemi başarısız oldu: {str(e)}")
        
        super().save_model(request, obj, form, change)
    
    def _process_approval(self, request, edit_request):
        """Helper to update User and Profile"""
        from django.db import transaction
        
        user = edit_request.user
        profile = user.profile
        
        # Note: first_name and last_name are not updated as they are not editable
        
        # Update Profile model
        profile.company_name = edit_request.company_name
        profile.phone_number = edit_request.phone_number
        profile.country = edit_request.country
        profile.city = edit_request.city
        profile.buyer_quarterly_volume = edit_request.buyer_quarterly_volume
        profile.producer_quarterly_sales = edit_request.producer_quarterly_sales
        profile.producer_product_count = edit_request.producer_product_count
        profile.save()
        
        # Update sectors
        if profile.is_buyer and edit_request.buyer_interested_sectors_ids:
            buyer_sectors = edit_request.get_buyer_sectors()
            if buyer_sectors.exists():
                profile.buyer_interested_sectors.set(buyer_sectors)
        
        if profile.is_producer and edit_request.producer_sectors_ids:
            producer_sectors = edit_request.get_producer_sectors()
            if producer_sectors.exists():
                profile.producer_sectors.set(producer_sectors)
        
        # Update request fields
        edit_request.reviewed_by = request.user
        edit_request.reviewed_at = timezone.now()
    
    def approve_profile_edits(self, request, queryset):
        """Approve selected profile edit requests"""
        from django.db import transaction
        
        approved_count = 0
        error_count = 0
        
        for edit_request in queryset.filter(status='pending'):
            try:
                with transaction.atomic():
                    self._process_approval(request, edit_request)
                    edit_request.status = 'approved'
                    edit_request.save()
                    approved_count += 1
            except Exception as e:
                error_count += 1
                messages.error(request, f"Error ({edit_request.user.username}): {str(e)}")
        
        if approved_count > 0:
            messages.success(request, f"✓ {approved_count} profile edit request(s) approved successfully!")
        if error_count > 0:
            messages.warning(request, f"⚠ {error_count} request(s) failed.")
    
    approve_profile_edits.short_description = "Approve selected profile edit requests"
    
    def reject_profile_edits(self, request, queryset):
        """Reject selected profile edit requests"""
        rejected_count = queryset.filter(status='pending').update(
            status='rejected',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        
        if rejected_count > 0:
            messages.success(request, f"{rejected_count} profile edit request(s) rejected.")
    
    reject_profile_edits.short_description = "Reject selected profile edit requests"


@admin.register(ProductRequest)
class ProductRequestAdmin(admin.ModelAdmin):
    list_display = (
        'get_title', 'producer', 'get_producer_company', 'status', 'created_at'
    )
    list_filter = ('status', 'created_at', 'is_active')
    search_fields = ('title_tr', 'title_en', 'description_tr', 'description_en', 'producer__username', 'producer__profile__company_name')
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
        """Display product title"""
        return obj.title_tr or obj.title_en or f"Product Request #{obj.id}"
    get_title.short_description = 'Ürün'
    
    def get_producer_company(self, obj):
        """Display producer company name"""
        if hasattr(obj.producer, 'profile'):
            return obj.producer.profile.company_name
        return '-'
    get_producer_company.short_description = 'Firma'
    
    def tags_display(self, obj):
        """Display tags"""
        tags = obj.get_tags()
        if tags.exists():
            return ', '.join([f"{t.name_tr} | {t.name_en}" for t in tags])
        return '-'
    tags_display.short_description = 'Etiketler'
    
    def photo1_preview(self, obj):
        if obj.photo1:
            return f'<img src="{obj.photo1.url}" style="max-width: 200px; max-height: 200px;" />'
        return '-'
    photo1_preview.short_description = 'Fotoğraf 1 Önizleme'
    photo1_preview.allow_tags = True
    
    def photo2_preview(self, obj):
        if obj.photo2:
            return f'<img src="{obj.photo2.url}" style="max-width: 200px; max-height: 200px;" />'
        return '-'
    photo2_preview.short_description = 'Fotoğraf 2 Önizleme'
    photo2_preview.allow_tags = True
    
    def photo3_preview(self, obj):
        if obj.photo3:
            return f'<img src="{obj.photo3.url}" style="max-width: 200px; max-height: 200px;" />'
        return '-'
    photo3_preview.short_description = 'Fotoğraf 3 Önizleme'
    photo3_preview.allow_tags = True
    
    def get_readonly_fields(self, request, obj=None):
        """Make all fields readonly except status and rejection_reason for pending requests"""
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
        """Handle status changes from the admin change form"""
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
        """Helper to create Product from ProductRequest"""
        from django.db import transaction
        
        # Create product
        product = Product.objects.create(
            producer=product_request.producer,
            sector=product_request.sector,
            title_tr=product_request.title_tr,
            title_en=product_request.title_en,
            description_tr=product_request.description_tr,
            description_en=product_request.description_en,
            photo1=product_request.photo1,
            photo2=product_request.photo2,
            photo3=product_request.photo3,
            is_active=product_request.is_active
        )
        
        # Add tags
        if product_request.tags_ids:
            tags = product_request.get_tags()
            if tags.exists():
                product.tags.set(tags)
        
        # Update request fields
        product_request.reviewed_by = request.user
        product_request.reviewed_at = timezone.now()
    
    def approve_products(self, request, queryset):
        """Approve selected product requests and create products"""
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
                messages.error(request, f"Error ({product_request.get_title(product_request)}): {str(e)}")
        
        if approved_count > 0:
            messages.success(request, f"✓ {approved_count} product request(s) approved successfully!")
        if error_count > 0:
            messages.warning(request, f"⚠ {error_count} request(s) failed.")
    
    approve_products.short_description = "Approve selected product requests"
    
    def reject_products(self, request, queryset):
        """Reject selected product requests"""
        rejected_count = queryset.filter(status='pending').update(
            status='rejected',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        
        if rejected_count > 0:
            messages.success(request, f"{rejected_count} product request(s) rejected.")
    
    reject_products.short_description = "Reject selected product requests"


@admin.register(ProductTag)
class ProductTagAdmin(admin.ModelAdmin):
    list_display = ('name_tr', 'name_en')
    search_fields = ('name_tr', 'name_en')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title_tr', 'title_en', 'producer', 'sector', 'is_active', 'created_at')
    list_filter = ('is_active', 'sector', 'created_at', 'tags')
    search_fields = ('title_tr', 'title_en', 'description_tr', 'description_en', 'producer__username')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('tags',)
    
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
            return f'<img src="{obj.image.url}" style="max-width: 300px; max-height: 300px;" />'
        return '-'
    image_preview.short_description = 'Görsel Önizleme'
    image_preview.allow_tags = True


@admin.register(ExpoSignup)
class ExpoSignupAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_user_company', 'expo', 'product_count', 'uses_listed_products', 'status', 'created_at')
    list_filter = ('status', 'uses_listed_products', 'expo', 'created_at')
    search_fields = ('user__username', 'user__email', 'user__profile__company_name', 'expo__title_tr', 'expo__title_en')
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
        """Display user's company name"""
        if hasattr(obj.user, 'profile'):
            return obj.user.profile.company_name
        return '-'
    get_user_company.short_description = 'Firma'
    
    def selected_products_display(self, obj):
        """Display selected products"""
        products = obj.selected_products.all()
        if products.exists():
            return ', '.join([p.title_tr or p.title_en for p in products])
        return '-'
    selected_products_display.short_description = 'Seçilen Ürünler'
