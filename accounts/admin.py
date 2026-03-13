from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils import timezone
from django.contrib import messages
from django.utils.html import format_html, mark_safe
from .models import Tenant, UserProfile, SignupRequest, SignupRequestHistory, ProfileEditRequest, MembershipConsent, ConsentText, ContactSubmission, TenantPhoto, TenantPhotoRequest, TenantLogoRequest


class SignupRequestHistoryInline(admin.TabularInline):
    """Read-only inline showing field-level change history for a SignupRequest."""
    model = SignupRequestHistory
    extra = 0
    can_delete = False
    show_change_link = False
    readonly_fields = ('changed_at', 'changed_by', 'changes_display')
    fields = ('changed_at', 'changed_by', 'changes_display')
    ordering = ('-changed_at',)
    verbose_name = "Değişiklik Kaydı"
    verbose_name_plural = "Değişiklik Geçmişi"

    def has_add_permission(self, request, obj=None):
        return False

    def changes_display(self, obj):
        if not obj.changes:
            return '-'
        rows = []
        for entry in obj.changes:
            label = entry.get('label') or entry.get('field', '')
            old_val = entry.get('old', '')
            new_val = entry.get('new', '')
            rows.append(
                format_html(
                    '<tr>'
                    '<td style="padding:4px 10px;font-weight:600;color:#374151;">{}</td>'
                    '<td style="padding:4px 10px;color:#dc2626;text-decoration:line-through;">{}</td>'
                    '<td style="padding:4px 10px;color:#374151;">&#8594;</td>'
                    '<td style="padding:4px 10px;color:#16a34a;">{}</td>'
                    '</tr>',
                    label, old_val, new_val,
                )
            )
        return format_html(
            '<table style="border-collapse:collapse;font-size:0.88rem;">'
            '<thead><tr>'
            '<th style="padding:4px 10px;text-align:left;color:#6b7280;">Alan</th>'
            '<th style="padding:4px 10px;text-align:left;color:#6b7280;">Eski De&#287;er</th>'
            '<th style="padding:4px 10px;"></th>'
            '<th style="padding:4px 10px;text-align:left;color:#6b7280;">Yeni De&#287;er</th>'
            '</tr></thead><tbody>{}</tbody></table>',
            mark_safe(''.join(rows)),
        )

    changes_display.short_description = "De&#287;i&#351;iklikler"


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
        'buyer_interested_sectors_display', 'producer_sectors_display',
        'consent_given', 'consent_timestamp', 'consent_ip',
        'username', 'email',
    )

    fieldsets = (
        ('Request Status', {
            'fields': ('status', 'reviewed_by', 'reviewed_at', 'rejection_reason')
        }),
        ('User Account Information', {
            'fields': ('username', 'email', 'first_name', 'last_name', 'password_hash')
        }),
        ('Company Information', {
            'fields': ('company_name', 'phone_number', 'country', 'city', 'open_address', 'website', 'about_company')
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
        ('\u00dcyelik Onay\u0131 (Hukuki Kay\u0131t)', {
            'fields': ('consent_given', 'consent_timestamp', 'consent_ip'),
            'description': 'Bu bilgiler kullan\u0131c\u0131 kayd\u0131 s\u0131ras\u0131nda otomatik olarak kaydedilir ve de\u011fi\u015ftirilemez.',
        }),
    )

    inlines = [SignupRequestHistoryInline]
    actions = ['approve_signups', 'reject_signups']

    _TRACKED_FIELDS = {
        'first_name': 'Ad',
        'last_name': 'Soyad',
        'company_name': 'Firma Adı',
        'phone_number': 'Telefon',
        'country': 'Ülke',
        'city': 'Şehir',
        'open_address': 'Açık Adres',
        'website': 'Web Sitesi',
        'about_company': 'Firma Hakkında',
        'is_buyer': 'Alıcı',
        'is_producer': 'Üretici',
        'buyer_interested_sectors_ids': 'İlgilenilen Sektör ID\'leri',
        'buyer_quarterly_volume': 'Çeyreklik Alım Hacmi',
        'producer_sectors_ids': 'Sektör ID\'leri',
        'producer_quarterly_sales': 'Çeyreklik Satış Hacmi',
        'producer_product_count': 'Ürün Sayısı',
        'status': 'Durum',
        'rejection_reason': 'Red Nedeni',
    }

    def buyer_interested_sectors_display(self, obj):
        sectors = obj.get_buyer_sectors()
        if sectors.exists():
            return ', '.join([f"{s.name_tr} | {s.name_en}" for s in sectors])
        return '-'
    buyer_interested_sectors_display.short_description = 'İlgilenilen Sektörler'

    def producer_sectors_display(self, obj):
        sectors = obj.get_producer_sectors()
        if sectors.exists():
            return ', '.join([f"{s.name_tr} | {s.name_en}" for s in sectors])
        return '-'
    producer_sectors_display.short_description = 'Sektörler'

    def get_readonly_fields(self, request, obj=None):
        return (
            'created_at', 'updated_at', 'reviewed_by', 'reviewed_at', 'password_hash',
            'username', 'email',
            'buyer_interested_sectors_display', 'producer_sectors_display',
            'consent_given', 'consent_timestamp', 'consent_ip',
        )

    def save_model(self, request, obj, form, change):
        old_instance = None
        if change and obj.pk:
            try:
                old_instance = SignupRequest.objects.get(pk=obj.pk)
            except SignupRequest.DoesNotExist:
                pass

        if change and 'status' in form.changed_data and obj.status == 'approved':
            try:
                if old_instance and old_instance.status == 'pending':
                    self._process_approval(request, obj)
            except Exception as e:
                obj.status = 'pending'
                obj.reviewed_by = None
                obj.reviewed_at = None
                messages.error(request, f"Onay işlemi başarısız oldu: {str(e)}")

        super().save_model(request, obj, form, change)

        if change and old_instance and form.changed_data:
            changed_entries = []
            for field in form.changed_data:
                if field not in self._TRACKED_FIELDS:
                    continue
                label = self._TRACKED_FIELDS[field]
                old_val = getattr(old_instance, field, '')
                new_val = getattr(obj, field, '')
                old_str = str(old_val) if old_val not in (None, '') else '—'
                new_str = str(new_val) if new_val not in (None, '') else '—'
                if old_str != new_str:
                    changed_entries.append({
                        'field': field,
                        'label': label,
                        'old': old_str,
                        'new': new_str,
                    })
            if changed_entries:
                SignupRequestHistory.objects.create(
                    signup_request=obj,
                    changed_by=request.user,
                    changes=changed_entries,
                )

    def _process_approval(self, request, signup_request):
        if User.objects.filter(username=signup_request.username).exists():
            raise ValueError(f"Username '{signup_request.username}' already exists")

        if User.objects.filter(email=signup_request.email).exists():
            raise ValueError(f"Email '{signup_request.email}' already exists")

        tenant = Tenant.objects.create(
            company_name=signup_request.company_name,
            phone_number=signup_request.phone_number,
            country=signup_request.country,
            city=signup_request.city,
            open_address=signup_request.open_address or '',
            website=signup_request.website or '',
            about_company=signup_request.about_company or '',
            is_buyer=signup_request.is_buyer,
            is_producer=signup_request.is_producer,
            buyer_quarterly_volume=signup_request.buyer_quarterly_volume,
            producer_quarterly_sales=signup_request.producer_quarterly_sales,
            producer_product_count=signup_request.producer_product_count,
        )

        if signup_request.buyer_interested_sectors_ids:
            buyer_sectors = signup_request.get_buyer_sectors()
            if buyer_sectors.exists():
                tenant.buyer_interested_sectors.set(buyer_sectors)

        if signup_request.producer_sectors_ids:
            producer_sectors = signup_request.get_producer_sectors()
            if producer_sectors.exists():
                tenant.producer_sectors.set(producer_sectors)

        user = User.objects.create(
            username=signup_request.username,
            email=signup_request.email,
            first_name=signup_request.first_name,
            last_name=signup_request.last_name,
            password=signup_request.password_hash
        )

        tenant.owner = user
        tenant.save(update_fields=['owner'])

        UserProfile.objects.create(user=user, tenant=tenant, tenant_role='admin')

        signup_request.reviewed_by = request.user
        signup_request.reviewed_at = timezone.now()

    def approve_signups(self, request, queryset):
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
        rejected_count = queryset.filter(status='pending').update(
            status='rejected',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )

        if rejected_count > 0:
            messages.success(request, f"{rejected_count} signup request(s) rejected.")

    reject_signups.short_description = "Reject selected signup requests"


class TenantMemberInline(admin.TabularInline):
    model = UserProfile
    extra = 0
    can_delete = True
    verbose_name = "Üye"
    verbose_name_plural = "Firma Üyeleri"
    fields = ('user', 'tenant_role', 'created_at')
    readonly_fields = ('created_at',)
    show_change_link = True

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        original_init = formset.form.__init__

        def patched_init(self_form, *args, **form_kwargs):
            original_init(self_form, *args, **form_kwargs)
            if 'user' not in self_form.fields:
                return
            taken = UserProfile.objects.values_list('user_id', flat=True)
            instance = self_form.instance
            if instance and instance.pk:
                self_form.fields['user'].disabled = True
                self_form.fields['user'].queryset = User.objects.filter(pk=instance.user_id)
            else:
                self_form.fields['user'].queryset = User.objects.exclude(
                    id__in=taken
                ).order_by('username')

        formset.form.__init__ = patched_init
        return formset


class TenantPhotoInline(admin.TabularInline):
    model = TenantPhoto
    extra = 0
    can_delete = True
    verbose_name = "Galeri Fotoğrafı"
    verbose_name_plural = "Galeri Fotoğrafları (Onaylı)"
    fields = ('photo', 'caption_tr', 'caption_en', 'order')
    readonly_fields = ()


class TenantLogoRequestInline(admin.TabularInline):
    model = TenantLogoRequest
    extra = 0
    can_delete = False
    show_change_link = True
    verbose_name = "Logo Talebi"
    verbose_name_plural = "Logo Talepleri"
    fields = ('logo', 'submitted_by', 'status', 'created_at')
    readonly_fields = ('logo', 'submitted_by', 'status', 'created_at')

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'owner_display', 'country', 'city', 'is_buyer', 'is_producer', 'show_company_profile', 'member_count', 'created_at')
    list_filter = ('is_buyer', 'is_producer', 'show_company_profile', 'country')
    search_fields = ('company_name', 'phone_number', 'city', 'owner__username', 'owner__email')
    readonly_fields = ('created_at', 'updated_at', 'owner_display', 'logo_preview')
    filter_horizontal = ('buyer_interested_sectors', 'producer_sectors')
    inlines = [TenantMemberInline, TenantPhotoInline, TenantLogoRequestInline]

    fieldsets = (
        ('Company Information', {
            'fields': (
                'company_name', 'company_username', 'phone_number', 'company_email',
                'country', 'city', 'open_address', 'website', 'about_company'
            )
        }),
        ('Company Profile Page', {
            'fields': ('show_company_profile', 'logo', 'logo_preview'),
            'description': 'Firma profil sayfası ayarları. Logo yüklemek için dosyayı seçin ve kaydedin.'
        }),
        ('Ownership', {
            'fields': ('owner', 'owner_display'),
        }),
        ('Tenant Type', {
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

    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" style="max-width:200px;max-height:200px;border-radius:8px;border:1px solid #e2e8f0;" />',
                obj.logo.url
            )
        return '-'
    logo_preview.short_description = 'Mevcut Logo Önizleme'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'owner':
            tenant_id = request.resolver_match.kwargs.get('object_id')
            if tenant_id:
                member_user_ids = UserProfile.objects.filter(
                    tenant_id=tenant_id
                ).values_list('user_id', flat=True)
                kwargs['queryset'] = User.objects.filter(id__in=member_user_ids).order_by('username')
            else:
                kwargs['queryset'] = User.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def owner_display(self, obj):
        if not obj.owner:
            return '-'
        return format_html(
            '<strong>{}</strong> &lt;{}&gt;',
            obj.owner.get_full_name() or obj.owner.username,
            obj.owner.email,
        )
    owner_display.short_description = 'Firma Hesabı Sahibi'

    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = 'Üye Sayısı'


@admin.register(TenantLogoRequest)
class TenantLogoRequestAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'submitted_by', 'status', 'created_at', 'logo_preview_small')
    list_filter = ('status', 'created_at')
    search_fields = ('tenant__company_name', 'submitted_by__username')
    readonly_fields = ('created_at', 'updated_at', 'reviewed_by', 'reviewed_at', 'logo_preview', 'tenant', 'submitted_by', 'logo')
    actions = ['approve_logos', 'reject_logos']

    fieldsets = (
        ('Talep Durumu', {
            'fields': ('status', 'reviewed_by', 'reviewed_at', 'rejection_reason')
        }),
        ('Firma ve Kullanıcı', {
            'fields': ('tenant', 'submitted_by')
        }),
        ('Logo', {
            'fields': ('logo', 'logo_preview')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" style="max-width:300px;max-height:300px;border-radius:8px;" />',
                obj.logo.url
            )
        return '-'
    logo_preview.short_description = 'Logo Önizleme'

    def logo_preview_small(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" style="max-width:60px;max-height:60px;border-radius:4px;" />',
                obj.logo.url
            )
        return '-'
    logo_preview_small.short_description = 'Logo'

    def _process_approval(self, request, logo_request):
        tenant = logo_request.tenant
        tenant.logo = logo_request.logo
        tenant.save(update_fields=['logo'])
        logo_request.reviewed_by = request.user
        logo_request.reviewed_at = timezone.now()

    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data and obj.status == 'approved':
            try:
                old = TenantLogoRequest.objects.get(pk=obj.pk)
                if old.status == 'pending':
                    self._process_approval(request, obj)
            except Exception as e:
                obj.status = 'pending'
                obj.reviewed_by = None
                obj.reviewed_at = None
                messages.error(request, f"Onay işlemi başarısız oldu: {str(e)}")
        super().save_model(request, obj, form, change)

    def approve_logos(self, request, queryset):
        from django.db import transaction
        approved_count = 0
        error_count = 0
        for logo_request in queryset.filter(status='pending'):
            try:
                with transaction.atomic():
                    self._process_approval(request, logo_request)
                    logo_request.status = 'approved'
                    logo_request.save()
                    approved_count += 1
            except Exception as e:
                error_count += 1
                messages.error(request, f"Error ({logo_request.tenant}): {str(e)}")
        if approved_count:
            messages.success(request, f"✓ {approved_count} logo request(s) approved!")
        if error_count:
            messages.warning(request, f"⚠ {error_count} request(s) failed.")
    approve_logos.short_description = "Approve selected logo requests"

    def reject_logos(self, request, queryset):
        rejected_count = queryset.filter(status='pending').update(
            status='rejected',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        if rejected_count:
            messages.success(request, f"{rejected_count} logo request(s) rejected.")
    reject_logos.short_description = "Reject selected logo requests"


@admin.register(TenantPhotoRequest)
class TenantPhotoRequestAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'submitted_by', 'status', 'created_at', 'photo_preview_small')
    list_filter = ('status', 'created_at')
    search_fields = ('tenant__company_name', 'submitted_by__username')
    readonly_fields = ('created_at', 'updated_at', 'reviewed_by', 'reviewed_at', 'photo_preview', 'tenant', 'submitted_by', 'photo', 'caption_tr', 'caption_en')
    actions = ['approve_photos', 'reject_photos']

    fieldsets = (
        ('Talep Durumu', {
            'fields': ('status', 'reviewed_by', 'reviewed_at', 'rejection_reason')
        }),
        ('Firma ve Kullanıcı', {
            'fields': ('tenant', 'submitted_by')
        }),
        ('Fotoğraf', {
            'fields': ('photo', 'photo_preview', 'caption_tr', 'caption_en')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="max-width:300px;max-height:300px;border-radius:8px;" />',
                obj.photo.url
            )
        return '-'
    photo_preview.short_description = 'Fotoğraf Önizleme'

    def photo_preview_small(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="max-width:60px;max-height:60px;border-radius:4px;" />',
                obj.photo.url
            )
        return '-'
    photo_preview_small.short_description = 'Fotoğraf'

    def _process_approval(self, request, photo_request):
        current_count = TenantPhoto.objects.filter(tenant=photo_request.tenant).count()
        if current_count >= 10:
            raise ValueError("Bu firma için maksimum 10 galeri fotoğrafı sınırına ulaşıldı.")
        TenantPhoto.objects.create(
            tenant=photo_request.tenant,
            photo=photo_request.photo,
            caption_tr=photo_request.caption_tr,
            caption_en=photo_request.caption_en,
        )
        photo_request.reviewed_by = request.user
        photo_request.reviewed_at = timezone.now()

    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data and obj.status == 'approved':
            try:
                old = TenantPhotoRequest.objects.get(pk=obj.pk)
                if old.status == 'pending':
                    self._process_approval(request, obj)
            except Exception as e:
                obj.status = 'pending'
                obj.reviewed_by = None
                obj.reviewed_at = None
                messages.error(request, f"Onay işlemi başarısız oldu: {str(e)}")
        super().save_model(request, obj, form, change)

    def approve_photos(self, request, queryset):
        from django.db import transaction
        approved_count = 0
        error_count = 0
        for photo_request in queryset.filter(status='pending'):
            try:
                with transaction.atomic():
                    self._process_approval(request, photo_request)
                    photo_request.status = 'approved'
                    photo_request.save()
                    approved_count += 1
            except Exception as e:
                error_count += 1
                messages.error(request, f"Error ({photo_request.tenant}): {str(e)}")
        if approved_count:
            messages.success(request, f"✓ {approved_count} photo request(s) approved!")
        if error_count:
            messages.warning(request, f"⚠ {error_count} request(s) failed.")
    approve_photos.short_description = "Approve selected photo requests"

    def reject_photos(self, request, queryset):
        rejected_count = queryset.filter(status='pending').update(
            status='rejected',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        if rejected_count:
            messages.success(request, f"{rejected_count} photo request(s) rejected.")
    reject_photos.short_description = "Reject selected photo requests"


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name = "Profil / Firma Bağlantısı"
    verbose_name_plural = "Profil / Firma Bağlantısı"
    fields = ('tenant', 'tenant_role')
    raw_id_fields = ('tenant',)


admin.site.unregister(User)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)


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
        if hasattr(obj.user, 'profile') and obj.user.profile.tenant:
            return obj.user.profile.tenant.company_name
        return '-'
    get_user_company.short_description = 'Mevcut Firma'

    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'E-posta'

    def buyer_interested_sectors_display(self, obj):
        sectors = obj.get_buyer_sectors()
        if sectors.exists():
            return ', '.join([f"{s.name_tr} | {s.name_en}" for s in sectors])
        return '-'
    buyer_interested_sectors_display.short_description = 'İlgilenilen Sektörler'

    def producer_sectors_display(self, obj):
        sectors = obj.get_producer_sectors()
        if sectors.exists():
            return ', '.join([f"{s.name_tr} | {s.name_en}" for s in sectors])
        return '-'
    producer_sectors_display.short_description = 'Sektörler'

    def get_readonly_fields(self, request, obj=None):
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
        user = edit_request.user
        tenant = user.profile.tenant

        tenant.company_name = edit_request.company_name
        tenant.phone_number = edit_request.phone_number
        tenant.country = edit_request.country
        tenant.city = edit_request.city
        tenant.open_address = edit_request.open_address
        tenant.buyer_quarterly_volume = edit_request.buyer_quarterly_volume
        tenant.producer_quarterly_sales = edit_request.producer_quarterly_sales
        tenant.producer_product_count = edit_request.producer_product_count
        tenant.save()

        if tenant.is_buyer and edit_request.buyer_interested_sectors_ids:
            buyer_sectors = edit_request.get_buyer_sectors()
            if buyer_sectors.exists():
                tenant.buyer_interested_sectors.set(buyer_sectors)

        if tenant.is_producer and edit_request.producer_sectors_ids:
            producer_sectors = edit_request.get_producer_sectors()
            if producer_sectors.exists():
                tenant.producer_sectors.set(producer_sectors)

        edit_request.reviewed_by = request.user
        edit_request.reviewed_at = timezone.now()

    def approve_profile_edits(self, request, queryset):
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
        rejected_count = queryset.filter(status='pending').update(
            status='rejected',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )

        if rejected_count > 0:
            messages.success(request, f"{rejected_count} profile edit request(s) rejected.")

    reject_profile_edits.short_description = "Reject selected profile edit requests"


@admin.register(MembershipConsent)
class MembershipConsentAdmin(admin.ModelAdmin):
    """Read-only admin for permanent membership consent audit records."""
    list_display = (
        'company_name', 'username', 'email',
        'consent_given_at', 'ip_address', 'consent_text_version'
    )
    list_filter = ('consent_given_at', 'consent_text_version')
    search_fields = ('username', 'email', 'company_name', 'ip_address')
    readonly_fields = (
        'signup_request', 'username', 'email', 'company_name',
        'consent_given_at', 'ip_address', 'consent_text_version'
    )
    ordering = ('-consent_given_at',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    class Meta:
        verbose_name = "Üyelik Onay Kaydı"
        verbose_name_plural = "Üyelik Onay Kayıtları"


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    """Read-only admin for contact form submission audit records."""
    list_display   = ('name', 'email', 'subject', 'ip_address', 'email_sent', 'submitted_at')
    list_filter    = ('email_sent', 'submitted_at')
    search_fields  = ('name', 'email', 'subject', 'message', 'ip_address')
    readonly_fields = ('name', 'email', 'phone', 'subject', 'message', 'ip_address', 'submitted_at', 'email_sent')
    ordering = ('-submitted_at',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(ConsentText)
class ConsentTextAdmin(admin.ModelAdmin):
    """Singleton admin – only one ConsentText record exists."""
    list_display = ('__str__', 'version', 'updated_at')
    readonly_fields = ('updated_at',)

    fieldsets = (
        ('Türkçe Metin', {
            'fields': ('text_tr',),
            'description': 'Kayıt formunda ve onay popup\'ında Türkçe olarak gösterilecek metin.'
        }),
        ('English Text', {
            'fields': ('text_en',),
            'description': 'English text shown in the registration form and confirmation popup.'
        }),
        ('Versiyon Bilgisi', {
            'fields': ('version', 'updated_at'),
            'description': 'Metni her değiştirdiğinizde versiyonu güncelleyin (örn. v1.0 → v1.1). '
                           'Bu değer kullanıcının onay kaydına işlenir.'
        }),
    )

    def has_add_permission(self, request):
        return not ConsentText.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = ConsentText.get_solo()
        from django.shortcuts import redirect
        from django.urls import reverse
        return redirect(
            reverse('admin:accounts_consenttext_change', args=[obj.pk])
        )
