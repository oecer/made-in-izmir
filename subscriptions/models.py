from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class SubscriptionPlan(models.Model):
    """Defines a subscription tier with feature flags and pricing."""

    # Bilingual identity
    name_tr = models.CharField(max_length=100, verbose_name="Plan Adı (TR)")
    name_en = models.CharField(max_length=100, verbose_name="Plan Adı (EN)")
    description_tr = models.TextField(blank=True, verbose_name="Açıklama (TR)")
    description_en = models.TextField(blank=True, verbose_name="Açıklama (EN)")

    # Pricing
    monthly_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name="Aylık Fiyat (TRY)"
    )

    # --- Feature flags ---
    show_company_profile = models.BooleanField(
        default=False,
        verbose_name="Firma Profil Sayfası",
        help_text="Firmanın genel profil sayfasının herkese açık olup olmayacağı."
    )
    company_username_editable = models.BooleanField(
        default=False,
        verbose_name="Firma URL'si Özelleştirme",
        help_text="Kullanıcının firma URL'sini (company_username) düzenleyip düzenleyemeyeceği."
    )
    has_business_card = models.BooleanField(
        default=False,
        verbose_name="Dijital Kartvizit",
        help_text="Firmanın dijital kartvizit sayfasının aktif olup olmadığı."
    )
    display_company_name = models.BooleanField(
        default=False,
        verbose_name="Firma Adı Görünürlüğü",
        help_text="Firma adının alıcı panosundaki ürün kartlarında ve ürün detay sayfasında görüntülenip görüntülenmeyeceği."
    )
    display_open_address = models.BooleanField(
        default=False,
        verbose_name="Açık Adres Görünürlüğü",
        help_text="Açık adresin ürün detay sayfasında görüntülenip görüntülenmeyeceği."
    )
    display_city = models.BooleanField(
        default=False,
        verbose_name="Şehir Görünürlüğü",
        help_text="Şehrin ürün detay sayfasında görüntülenip görüntülenmeyeceği."
    )
    display_phone = models.BooleanField(
        default=False,
        verbose_name="Telefon Görünürlüğü",
        help_text="Telefon numarasının ürün detay sayfasındaki iletişim formunda görüntülenip görüntülenmeyeceği."
    )
    display_email = models.BooleanField(
        default=False,
        verbose_name="E-posta Görünürlüğü",
        help_text="E-posta adresinin ürün detay sayfasındaki iletişim formunda görüntülenip görüntülenmeyeceği."
    )
    display_website = models.BooleanField(
        default=False,
        verbose_name="Web Sitesi Görünürlüğü",
        help_text="Web sitesinin ürün detay sayfasındaki iletişim formunda görüntülenip görüntülenmeyeceği."
    )
    viewer_sees_all = models.BooleanField(
        default=False,
        verbose_name="Tüm Üretici Bilgilerini Gör",
        help_text="Bu plana sahip kullanıcı, diğer üreticilerin abonelik planından bağımsız olarak tüm firma adı, adres, şehir, telefon, e-posta ve web sitesi bilgilerini görebilir."
    )

    # --- Limits ---
    max_active_products = models.PositiveIntegerField(
        null=True, blank=True,
        verbose_name="Maksimum Aktif Ürün Sayısı",
        help_text="Boş bırakılırsa sınırsız ürün aktif edilebilir."
    )

    # Display / meta
    display_order = models.PositiveSmallIntegerField(default=0, verbose_name="Sıralama")
    is_active = models.BooleanField(default=True, verbose_name="Aktif Plan")

    class Meta:
        verbose_name = "Abonelik Planı"
        verbose_name_plural = "Abonelik Planları"
        ordering = ['display_order', 'monthly_price']
        db_table = 'subscriptions_plan'

    def __str__(self):
        price = f"{int(self.monthly_price):,} TRY/ay" if self.monthly_price else "Ücretsiz"
        return f"{self.name_tr} ({price})"

    def get_price_display(self):
        if not self.monthly_price:
            return "Ücretsiz"
        return f"{int(self.monthly_price):,} TRY/ay"


class TenantSubscription(models.Model):
    """Links a Tenant to a SubscriptionPlan. One active subscription per tenant."""

    STATUS_CHOICES = [
        ('active', 'Aktif'),
        ('expired', 'Süresi Dolmuş'),
        ('cancelled', 'İptal Edildi'),
    ]

    tenant = models.OneToOneField(
        'accounts.Tenant',
        on_delete=models.CASCADE,
        related_name='subscription',
        verbose_name="Firma"
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name='subscriptions',
        verbose_name="Plan"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='active',
        verbose_name="Durum"
    )

    # Date tracking
    started_at = models.DateField(verbose_name="Başlangıç Tarihi")
    expires_at = models.DateField(
        null=True, blank=True,
        verbose_name="Bitiş Tarihi",
        help_text="Boş bırakılırsa abonelik süresiz olarak devam eder."
    )

    # Admin tracking
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assigned_subscriptions',
        verbose_name="Atayan Admin"
    )
    notes = models.TextField(blank=True, verbose_name="Notlar")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Firma Aboneliği"
        verbose_name_plural = "Firma Abonelikleri"
        ordering = ['-created_at']
        db_table = 'subscriptions_tenantsubscription'

    def __str__(self):
        return f"{self.tenant.company_name} → {self.plan.name_tr} ({self.get_status_display()})"

    def is_currently_active(self):
        """Check if subscription is active and not expired."""
        if self.status != 'active':
            return False
        if self.expires_at and self.expires_at < timezone.now().date():
            return False
        return True

    def get_effective_plan(self):
        """Return the active plan, or the Standard (free) fallback if expired/cancelled."""
        if self.is_currently_active():
            return self.plan
        return SubscriptionPlan.objects.filter(
            is_active=True, monthly_price=0
        ).order_by('display_order').first()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Sync show_company_profile on Tenant from the effective plan
        plan = self.get_effective_plan()
        if plan is not None:
            should_show = plan.show_company_profile
            if self.tenant.show_company_profile != should_show:
                self.tenant.show_company_profile = should_show
                self.tenant.save(update_fields=['show_company_profile'])


class PlanCampaign(models.Model):
    """
    A time-limited promotional campaign attached to a SubscriptionPlan.
    Used to display special offers on the producers page and for admin management.
    """
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.CASCADE,
        related_name='campaigns',
        verbose_name="Plan"
    )
    title_tr = models.CharField(max_length=200, verbose_name="Kampanya Başlığı (TR)")
    title_en = models.CharField(max_length=200, verbose_name="Kampanya Başlığı (EN)")
    description_tr = models.TextField(verbose_name="Açıklama (TR)")
    description_en = models.TextField(verbose_name="Açıklama (EN)")

    # Campaign window
    valid_from = models.DateField(verbose_name="Kampanya Başlangıcı")
    valid_until = models.DateField(verbose_name="Kampanya Bitiş Tarihi")

    # Trial duration granted when a company signs up during campaign
    trial_months = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Ücretsiz Deneme Süresi (Ay)",
        help_text="Kampanya kapsamında verilen ücretsiz deneme süresi (ay). 0 ise deneme yok."
    )

    is_active = models.BooleanField(default=True, verbose_name="Aktif")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Plan Kampanyası"
        verbose_name_plural = "Plan Kampanyaları"
        ordering = ['-valid_until']
        db_table = 'subscriptions_plancampaign'

    def __str__(self):
        return f"{self.plan.name_tr} — {self.title_tr} ({self.valid_until})"

    def is_currently_valid(self):
        today = timezone.now().date()
        return self.is_active and self.valid_from <= today <= self.valid_until
