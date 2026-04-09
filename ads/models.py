import os
import uuid
from datetime import date

from django.db import models


def ad_image_upload_to(instance, filename):
    ext = os.path.splitext(filename)[1].lower() or '.jpg'
    short_id = uuid.uuid4().hex[:8]
    return f'ads/{instance.slot.slug}_{short_id}{ext}'


class AdSlot(models.Model):
    AD_TYPE_HORIZONTAL = 'horizontal'
    AD_TYPE_GRID_CARD = 'grid_card'
    AD_TYPE_CHOICES = [
        (AD_TYPE_HORIZONTAL, 'Yatay Banner'),
        (AD_TYPE_GRID_CARD, 'Grid Kartı'),
    ]

    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    width_px = models.PositiveIntegerField()
    height_px = models.PositiveIntegerField()
    ad_type = models.CharField(max_length=20, choices=AD_TYPE_CHOICES)
    is_active = models.BooleanField(default=True)

    # Grid-card specific settings
    grid_interval = models.PositiveIntegerField(
        default=6,
        help_text='Her kaç üründen sonra reklam gösterileceği (yalnızca grid_card tipi için)',
    )
    max_ads_in_grid = models.PositiveIntegerField(
        default=3,
        help_text='Grid içinde maksimum gösterilecek reklam sayısı (referans)',
    )

    # Pricing
    price_daily = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        verbose_name='Günlük Fiyat',
    )
    price_weekly = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        verbose_name='Haftalık Fiyat',
    )
    price_monthly = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        verbose_name='Aylık Fiyat',
    )
    price_currency = models.CharField(
        max_length=3, default='TRY',
        verbose_name='Para Birimi',
        help_text='Örn: TRY, USD, EUR',
    )

    class Meta:
        verbose_name = 'Reklam Slotu'
        verbose_name_plural = 'Reklam Slotları'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.width_px}×{self.height_px} px)'

    @property
    def dimensions(self):
        return f'{self.width_px}×{self.height_px} px'


class Ad(models.Model):
    slot = models.ForeignKey(
        AdSlot, on_delete=models.CASCADE,
        related_name='ads', verbose_name='Slot',
    )
    advertiser_name = models.CharField(max_length=200, verbose_name='Reklamveren')
    image = models.ImageField(
        upload_to=ad_image_upload_to, blank=True, null=True,
        verbose_name='Görsel',
        help_text='Boş bırakılırsa CSS placeholder gösterilir',
    )
    link_url = models.CharField(
        max_length=500, default='#',
        verbose_name='Hedef URL',
        help_text='Reklama tıklandığında yönlendirilecek adres',
    )
    title = models.CharField(
        max_length=200, blank=True,
        verbose_name='Başlık / Alt Metin',
        help_text='Görselin alt metni ve tooltip olarak kullanılır',
    )
    start_date = models.DateField(verbose_name='Başlangıç Tarihi')
    end_date = models.DateField(verbose_name='Bitiş Tarihi')
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Sıralama',
        help_text='Küçük değer önce gösterilir',
    )
    display_duration_seconds = models.PositiveIntegerField(
        default=5,
        verbose_name='Gösterim Süresi (sn)',
        help_text='Bu reklamın rotasyonda kaç saniye gösterileceği.',
    )
    is_active = models.BooleanField(default=True, verbose_name='Aktif')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Reklam'
        verbose_name_plural = 'Reklamlar'
        ordering = ['slot', 'order']

    def __str__(self):
        return f'{self.advertiser_name} – {self.slot.name}'

    @property
    def is_currently_active(self):
        today = date.today()
        return self.is_active and self.start_date <= today <= self.end_date
