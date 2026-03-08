from django.db import models
from django.contrib.auth.models import User


class SignupRequest(models.Model):
    """Pending signup requests awaiting admin approval"""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    # User account information
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    password_hash = models.CharField(max_length=255)  # Hashed password

    # Company information
    company_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    open_address = models.TextField(blank=True, null=True)
    website = models.URLField(max_length=255, blank=True, null=True)
    about_company = models.TextField(blank=True, null=True)

    # User type
    is_buyer = models.BooleanField(default=False)
    is_producer = models.BooleanField(default=False)

    # Buyer-specific fields (stored as JSON-like text for sectors)
    buyer_interested_sectors_ids = models.TextField(blank=True, null=True)  # Comma-separated sector IDs
    buyer_quarterly_volume = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True
    )

    # Producer-specific fields
    producer_sectors_ids = models.TextField(blank=True, null=True)  # Comma-separated sector IDs
    producer_quarterly_sales = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True
    )
    producer_product_count = models.IntegerField(blank=True, null=True)

    # Membership consent (legal record)
    consent_given = models.BooleanField(default=False, verbose_name="Üyelik Onayı Verildi")
    consent_timestamp = models.DateTimeField(null=True, blank=True, verbose_name="Onay Tarihi/Saati")
    consent_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="Onay IP Adresi")

    # Request status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Admin actions
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_signups'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Kayıt Talebi"
        verbose_name_plural = "Kayıt Talepleri"
        ordering = ['-created_at']
        db_table = 'main_signuprequest'

    def __str__(self):
        return f"{self.username} - {self.company_name} ({self.get_status_display()})"

    def get_buyer_sectors(self):
        """Get buyer interested sectors as queryset"""
        from catalog.models import Sector
        if self.buyer_interested_sectors_ids:
            ids = [int(id.strip()) for id in self.buyer_interested_sectors_ids.split(',') if id.strip()]
            return Sector.objects.filter(id__in=ids)
        return Sector.objects.none()

    def get_producer_sectors(self):
        """Get producer sectors as queryset"""
        from catalog.models import Sector
        if self.producer_sectors_ids:
            ids = [int(id.strip()) for id in self.producer_sectors_ids.split(',') if id.strip()]
            return Sector.objects.filter(id__in=ids)
        return Sector.objects.none()


class SignupRequestHistory(models.Model):
    """Records field-level changes made by admins to SignupRequest objects."""

    signup_request = models.ForeignKey(
        'SignupRequest',
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name="Kayıt Talebi"
    )
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Değiştiren"
    )
    changed_at = models.DateTimeField(auto_now_add=True, verbose_name="Değiştirilme Tarihi")
    # JSON list of {"field": ..., "label": ..., "old": ..., "new": ...}
    changes = models.JSONField(verbose_name="Değişiklikler")

    class Meta:
        verbose_name = "Kayıt Talebi Geçmişi"
        verbose_name_plural = "Kayıt Talebi Geçmişi"
        ordering = ['-changed_at']
        db_table = 'main_signuprequesthistory'

    def __str__(self):
        return f"#{self.signup_request_id} – {self.changed_at.strftime('%d.%m.%Y %H:%M')} – {self.changed_by}"


class ConsentText(models.Model):
    """Singleton model – stores the editable membership consent text shown during signup."""

    text_tr = models.TextField(
        verbose_name="Onay Metni (Türkçe)",
        help_text="Kayıt formunda ve onay popup'ında gösterilecek Türkçe metin."
    )
    text_en = models.TextField(
        verbose_name="Consent Text (English)",
        help_text="English text shown in the registration form and confirmation popup."
    )
    version = models.CharField(
        max_length=20,
        default='v1.0',
        verbose_name="Versiyon",
        help_text="Değişiklik yapıldığında versiyonu güncelleyin (örn. v1.1). Bu değer onay kayıtlarına işlenir."
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Son Güncelleme")

    class Meta:
        verbose_name = "Üyelik Onay Metni"
        verbose_name_plural = "Üyelik Onay Metni"  # Intentionally singular – singleton
        db_table = 'main_consenttext'

    def __str__(self):
        return f"Üyelik Onay Metni ({self.version}) – {self.updated_at.strftime('%d.%m.%Y')}"

    def save(self, *args, **kwargs):
        """Enforce singleton: only one ConsentText row may exist."""
        self.pk = 1  # Always overwrite the same row
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        """Return the single ConsentText instance, creating a default one if necessary."""
        obj, _ = cls.objects.get_or_create(
            pk=1,
            defaults={
                'text_tr': (
                    "Madeinİzmir platformuna üye olarak; kayıt sırasında ve sonrasında sisteme girdiğim tüm firma bilgileri, ürün bilgileri, logo, görsel ve diğer içeriklerin Madeinİzmir platformunda, gerek yurt içinde gerek yurt dışında tanıtım ve görünürlük amacıyla herkese açık şekilde yayınlanacağını bildiğimi ve kabul ettiğimi beyan ederim.\n\n"
                    "Yüklediğim tüm içeriklerin tarafıma ait olduğunu; telif hakkı, marka, patent, tasarım koruması, gizlilik veya üçüncü kişi haklarına tabi olması durumunda doğabilecek tüm hukuki ve cezai sorumluluğun tamamen tarafıma ait olduğunu kabul ederim.\n\n"
                    "Madeinİzmir'in, üye firma tarafından yüklenen içeriklerden kaynaklanan hiçbir hukuki sorumluluğu bulunmadığını kabul ederim.\n\n"
                    "Madeinİzmir platformunun firma tanıtımı, ticari görünürlük ve ihracata yönelik dijital vitrin amacıyla faaliyet gösterdiğini ve üyeliğimin bu kapsamda oluşturulduğunu kabul ederim."
                ),
                'text_en': (
                    "By becoming a member of the Madeinİzmir platform, I hereby acknowledge and accept that all company information, product details, logos, images, and other content that I provide during registration and thereafter will be published publicly on the Madeinİzmir platform for promotional and visibility purposes, both domestically and internationally.\n\n"
                    "I accept that all content uploaded by me belongs to my company and that any legal and criminal liability arising from copyright, trademark, patent, design rights, confidentiality obligations, or third-party rights related to such content rests entirely with me.\n\n"
                    "I accept that Madeinİzmir shall bear no legal responsibility for any content uploaded by member companies.\n\n"
                    "I acknowledge and accept that the Madeinİzmir platform operates as a digital showcase for company promotion, commercial visibility, and export-oriented presentation, and that my membership is established within this scope."
                ),
                'version': 'v1.0',
            }
        )
        return obj


class MembershipConsent(models.Model):
    """Permanent, immutable record of every membership consent event – must never be deleted."""

    # Reference to the pending signup request (kept even if request is deleted later)
    signup_request = models.ForeignKey(
        'SignupRequest',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='consent_records',
        verbose_name="Kayıt Talebi"
    )

    # Who gave consent (company info copied at the time of consent)
    username = models.CharField(max_length=150, verbose_name="Kullanıcı Adı")
    email = models.EmailField(verbose_name="E-posta")
    company_name = models.CharField(max_length=200, verbose_name="Firma Adı")

    # When and from where
    consent_given_at = models.DateTimeField(verbose_name="Onay Tarihi/Saati")
    ip_address = models.GenericIPAddressField(verbose_name="IP Adresi")

    # The exact text that was shown and accepted
    consent_text_version = models.CharField(
        max_length=50,
        default='v1.0',
        verbose_name="Onay Metni Versiyonu"
    )

    class Meta:
        verbose_name = "Üyelik Onay Kaydı"
        verbose_name_plural = "Üyelik Onay Kayıtları"
        ordering = ['-consent_given_at']
        db_table = 'main_membershipconsent'

    def __str__(self):
        return f"{self.company_name} ({self.username}) – {self.consent_given_at.strftime('%d.%m.%Y %H:%M')}"


class Tenant(models.Model):
    """Company/organization entity - the multi-tenancy unit"""

    # Owner (the primary contact / account holder)
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_tenants',
        verbose_name="Firma Hesabı Sahibi"
    )

    # Company information
    company_name = models.CharField(max_length=200, verbose_name="Firma Adı")
    company_username = models.SlugField(
        max_length=150,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Firma Kullanıcı Adı",
        help_text="URL'de kullanılacak benzersiz firma tanımlayıcısı (örn. izmir-tekstil)"
    )
    phone_number = models.CharField(max_length=20, verbose_name="Telefon Numarası")
    country = models.CharField(max_length=100, verbose_name="Ülke")
    city = models.CharField(max_length=100, verbose_name="Şehir")
    open_address = models.TextField(blank=True, null=True, verbose_name="Açık Adres")
    website = models.URLField(max_length=255, blank=True, null=True, verbose_name="Web Sitesi")
    about_company = models.TextField(blank=True, null=True, verbose_name="Firma Hakkında")

    # Tenant type (can be both)
    is_buyer = models.BooleanField(default=False, verbose_name="Alıcı")
    is_producer = models.BooleanField(default=False, verbose_name="Üretici")

    # Buyer-specific fields
    buyer_interested_sectors = models.ManyToManyField(
        'catalog.Sector',
        blank=True,
        related_name='interested_buyer_tenants',
        verbose_name="İlgilenilen Sektörler"
    )
    buyer_quarterly_volume = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Çeyreklik Alım Hacmi (USD)"
    )

    # Producer-specific fields
    producer_sectors = models.ManyToManyField(
        'catalog.Sector',
        blank=True,
        related_name='producer_tenants',
        verbose_name="Sektörler"
    )
    producer_quarterly_sales = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Çeyreklik Satış Hacmi (USD)"
    )
    producer_product_count = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Yaklaşık Ürün Sayısı"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Firma (Tenant)"
        verbose_name_plural = "Firmalar (Tenants)"
        ordering = ['company_name']
        db_table = 'main_tenant'

    def __str__(self):
        return self.company_name

    def get_tenant_types(self):
        types = []
        if self.is_buyer:
            types.append("Alıcı")
        if self.is_producer:
            types.append("Üretici")
        return ", ".join(types) if types else "Belirtilmemiş"


class UserProfile(models.Model):
    """Extended user profile - linked to a Tenant"""

    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('read_only', 'Read Only'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name='members',
        null=True, blank=True, verbose_name="Firma"
    )
    tenant_role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='admin',
        verbose_name="Firma Rolü"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Kullanıcı Profili"
        verbose_name_plural = "Kullanıcı Profilleri"
        db_table = 'main_userprofile'

    def __str__(self):
        tenant_name = self.tenant.company_name if self.tenant else '-'
        return f"{self.user.get_full_name()} - {tenant_name}"


class ContactSubmission(models.Model):
    """Audit log for contact form submissions that passed all spam checks."""

    name    = models.CharField(max_length=200, verbose_name="Ad Soyad")
    email   = models.EmailField(verbose_name="E-posta")
    phone   = models.CharField(max_length=50, blank=True, verbose_name="Telefon")
    subject = models.CharField(max_length=200, verbose_name="Konu")
    message = models.TextField(verbose_name="Mesaj")
    ip_address   = models.GenericIPAddressField(verbose_name="IP Adresi")
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="Gönderilme Zamanı")
    email_sent   = models.BooleanField(default=False, verbose_name="E-posta Gönderildi")

    class Meta:
        verbose_name = "İletişim Formu Başvurusu"
        verbose_name_plural = "İletişim Formu Başvuruları"
        ordering = ['-submitted_at']
        db_table = 'contact_submission'

    def __str__(self):
        return f"{self.name} <{self.email}> – {self.subject}"


class ProfileEditRequest(models.Model):
    """Pending profile edit requests awaiting admin approval"""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    # User who requested the edit
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='profile_edit_requests',
        verbose_name="Kullanıcı"
    )

    # Common fields (username and email cannot be changed)
    first_name = models.CharField(max_length=100, blank=True, verbose_name="Ad")
    last_name = models.CharField(max_length=100, blank=True, verbose_name="Soyad")
    company_name = models.CharField(max_length=200, blank=True, verbose_name="Firma Adı")
    phone_number = models.CharField(max_length=20, blank=True, verbose_name="Telefon Numarası")
    country = models.CharField(max_length=100, blank=True, verbose_name="Ülke")
    city = models.CharField(max_length=100, blank=True, verbose_name="Şehir")
    open_address = models.TextField(blank=True, null=True, verbose_name="Açık Adres")

    # Buyer-specific fields (stored as JSON-like text for sectors)
    buyer_interested_sectors_ids = models.TextField(blank=True, null=True, verbose_name="İlgilenilen Sektör ID'leri")
    buyer_quarterly_volume = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Çeyreklik Alım Hacmi (USD)"
    )

    # Producer-specific fields
    producer_sectors_ids = models.TextField(blank=True, null=True, verbose_name="Sektör ID'leri")
    producer_quarterly_sales = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Çeyreklik Satış Hacmi (USD)"
    )
    producer_product_count = models.IntegerField(blank=True, null=True, verbose_name="Yaklaşık Ürün Sayısı")

    # Request status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Durum")

    # Admin actions
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_profile_edits',
        verbose_name="İnceleyen"
    )
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name="İnceleme Tarihi")
    rejection_reason = models.TextField(blank=True, null=True, verbose_name="Red Nedeni")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Profil Düzenleme Talebi"
        verbose_name_plural = "Profil Düzenleme Talepleri"
        ordering = ['-created_at']
        db_table = 'main_profileeditrequest'

    def __str__(self):
        return f"{self.user.username} - Profil Düzenleme ({self.get_status_display()})"

    def get_buyer_sectors(self):
        """Get buyer interested sectors as queryset"""
        from catalog.models import Sector
        if self.buyer_interested_sectors_ids:
            ids = [int(id.strip()) for id in self.buyer_interested_sectors_ids.split(',') if id.strip()]
            return Sector.objects.filter(id__in=ids)
        return Sector.objects.none()

    def get_producer_sectors(self):
        """Get producer sectors as queryset"""
        from catalog.models import Sector
        if self.producer_sectors_ids:
            ids = [int(id.strip()) for id in self.producer_sectors_ids.split(',') if id.strip()]
            return Sector.objects.filter(id__in=ids)
        return Sector.objects.none()
