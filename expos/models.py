from django.db import models
from django.contrib.auth.models import User


class Expo(models.Model):
    """Trade fairs and expos"""
    # Multilingual fields
    title_tr = models.CharField(max_length=200, verbose_name="Fuar Başlığı (TR)")
    title_en = models.CharField(max_length=200, verbose_name="Fuar Başlığı (EN)")
    description_tr = models.TextField(verbose_name="Fuar Açıklaması (TR)")
    description_en = models.TextField(verbose_name="Fuar Açıklaması (EN)")

    # Location
    location_tr = models.CharField(max_length=200, verbose_name="Konum (TR)")
    location_en = models.CharField(max_length=200, verbose_name="Konum (EN)")

    # Dates
    start_date = models.DateField(verbose_name="Başlangıç Tarihi")
    end_date = models.DateField(verbose_name="Bitiş Tarihi")

    # Registration deadline
    registration_deadline = models.DateField(verbose_name="Kayıt Son Tarihi")

    # Image
    image = models.ImageField(upload_to='expos/', blank=True, null=True, verbose_name="Fuar Görseli")

    # Status
    is_active = models.BooleanField(default=True, verbose_name="Aktif")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Fuar"
        verbose_name_plural = "Fuarlar"
        ordering = ['start_date']
        db_table = 'main_expo'

    def __str__(self):
        return self.title_tr or self.title_en or f"Expo #{self.id}"

    def is_registration_open(self):
        """Check if registration is still open"""
        from django.utils import timezone
        return self.registration_deadline >= timezone.now().date()


class ExpoSignup(models.Model):
    """User signups for expos"""
    expo = models.ForeignKey(
        'Expo',
        on_delete=models.CASCADE,
        related_name='signups',
        verbose_name="Fuar"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='expo_signups',
        verbose_name="Kullanıcı"
    )
    # Tenant (owner company)
    tenant = models.ForeignKey(
        'accounts.Tenant',
        on_delete=models.CASCADE,
        related_name='expo_signups',
        null=True, blank=True,
        verbose_name="Firma"
    )

    # Product information
    product_count = models.IntegerField(verbose_name="Ürün Sayısı")
    uses_listed_products = models.BooleanField(
        default=False,
        verbose_name="Made in İzmir'de Listelenen Ürünler"
    )

    # If uses_listed_products is True, store selected product IDs
    selected_products = models.ManyToManyField(
        'catalog.Product',
        blank=True,
        related_name='expo_signups',
        verbose_name="Seçilen Ürünler"
    )

    # If uses_listed_products is False, store free text description
    product_description = models.TextField(
        blank=True,
        verbose_name="Ürün Açıklaması"
    )

    # Additional notes
    notes = models.TextField(blank=True, verbose_name="Notlar")

    # Status
    STATUS_CHOICES = [
        ('pending', 'Beklemede'),
        ('confirmed', 'Onaylandı'),
        ('cancelled', 'İptal Edildi'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Durum"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Fuar Kaydı"
        verbose_name_plural = "Fuar Kayıtları"
        ordering = ['-created_at']
        unique_together = ['expo', 'user']
        db_table = 'main_exposignup'

    def __str__(self):
        return f"{self.user.username} - {self.expo.title_tr} ({self.get_status_display()})"
