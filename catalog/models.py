from django.db import models
from django.contrib.auth.models import User


class Sector(models.Model):
    """Sectors list for categorizing buyers and producers"""
    name_tr = models.CharField(max_length=200, verbose_name="Sektör Adı (TR)")
    name_en = models.CharField(max_length=200, verbose_name="Sektör Adı (EN)")

    class Meta:
        verbose_name = "Sektör"
        verbose_name_plural = "Sektörler"
        ordering = ['name_tr']
        db_table = 'main_sector'

    def __str__(self):
        return self.name_tr


class ProductTag(models.Model):
    """Tags for categorizing products"""
    name_tr = models.CharField(max_length=100, verbose_name="Etiket Adı (TR)")
    name_en = models.CharField(max_length=100, verbose_name="Etiket Adı (EN)")

    class Meta:
        verbose_name = "Ürün Etiketi"
        verbose_name_plural = "Ürün Etiketleri"
        ordering = ['name_tr']
        db_table = 'main_producttag'

    def __str__(self):
        return self.name_tr


class ProductRequest(models.Model):
    """Pending product requests awaiting admin approval"""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    # Producer (who submitted)
    producer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='product_requests',
        verbose_name="Üretici"
    )
    # Tenant (owner company)
    tenant = models.ForeignKey(
        'accounts.Tenant',
        on_delete=models.CASCADE,
        related_name='product_requests',
        null=True, blank=True,
        verbose_name="Firma"
    )

    # Multilingual fields
    title_tr = models.CharField(max_length=200, blank=True, verbose_name="Ürün Başlığı (TR)")
    title_en = models.CharField(max_length=200, blank=True, verbose_name="Ürün Başlığı (EN)")
    description_tr = models.TextField(blank=True, verbose_name="Ürün Açıklaması (TR)")
    description_en = models.TextField(blank=True, verbose_name="Ürün Açıklaması (EN)")

    # Photos (max 3)
    photo1 = models.ImageField(upload_to='product_requests/', blank=True, null=True, verbose_name="Fotoğraf 1")
    photo2 = models.ImageField(upload_to='product_requests/', blank=True, null=True, verbose_name="Fotoğraf 2")
    photo3 = models.ImageField(upload_to='product_requests/', blank=True, null=True, verbose_name="Fotoğraf 3")

    # Tags (stored as comma-separated IDs)
    tags_ids = models.TextField(blank=True, null=True, verbose_name="Etiket ID'leri")

    # Sector
    sector = models.ForeignKey(
        'Sector',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='product_requests',
        verbose_name="Sektör"
    )

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Durum")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")

    # Admin actions
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_products',
        verbose_name="İnceleyen"
    )
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name="İnceleme Tarihi")
    rejection_reason = models.TextField(blank=True, null=True, verbose_name="Red Nedeni")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ürün Talebi"
        verbose_name_plural = "Ürün Talepleri"
        ordering = ['-created_at']
        db_table = 'main_productrequest'

    def __str__(self):
        title = self.title_tr or self.title_en or f"Product Request #{self.id}"
        return f"{title} - {self.producer.username} ({self.get_status_display()})"

    def get_tags(self):
        """Get tags as queryset"""
        if self.tags_ids:
            ids = [int(id.strip()) for id in self.tags_ids.split(',') if id.strip()]
            return ProductTag.objects.filter(id__in=ids)
        return ProductTag.objects.none()

    def save(self, *args, **kwargs):
        """Override save to compress images before saving"""
        from django.conf import settings
        from .utils import compress_image

        if getattr(settings, 'IMAGE_COMPRESS_ENABLED', True):
            max_size = getattr(settings, 'IMAGE_MAX_SIZE', (1920, 1920))
            quality = getattr(settings, 'IMAGE_QUALITY', 85)

            if self.photo1 and not self.pk:
                self.photo1 = compress_image(self.photo1, max_size, quality)
            if self.photo2 and not self.pk:
                self.photo2 = compress_image(self.photo2, max_size, quality)
            if self.photo3 and not self.pk:
                self.photo3 = compress_image(self.photo3, max_size, quality)

        super().save(*args, **kwargs)


class Product(models.Model):
    """Products created by producers"""
    producer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="Üretici"
    )
    # Tenant (owner company)
    tenant = models.ForeignKey(
        'accounts.Tenant',
        on_delete=models.CASCADE,
        related_name='products',
        null=True, blank=True,
        verbose_name="Firma"
    )

    # Multilingual fields
    title_tr = models.CharField(max_length=200, blank=True, verbose_name="Ürün Başlığı (TR)")
    title_en = models.CharField(max_length=200, blank=True, verbose_name="Ürün Başlığı (EN)")
    description_tr = models.TextField(blank=True, verbose_name="Ürün Açıklaması (TR)")
    description_en = models.TextField(blank=True, verbose_name="Ürün Açıklaması (EN)")

    # Photos (max 3)
    photo1 = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Fotoğraf 1")
    photo2 = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Fotoğraf 2")
    photo3 = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Fotoğraf 3")

    # Tags (max 3)
    tags = models.ManyToManyField(
        'ProductTag',
        blank=True,
        related_name='products',
        verbose_name="Etiketler"
    )

    # Sector
    sector = models.ForeignKey(
        'Sector',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name="Sektör"
    )

    # Status
    is_active = models.BooleanField(default=True, verbose_name="Aktif")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ürün"
        verbose_name_plural = "Ürünler"
        ordering = ['-created_at']
        db_table = 'main_product'

    def __str__(self):
        return self.title_tr or self.title_en or f"Product #{self.id}"

    def get_tags(self):
        """Get tags as queryset - added for consistency with ProductRequest"""
        return self.tags.all()

    def clean(self):
        """Validate that at least one title is provided"""
        from django.core.exceptions import ValidationError
        if not self.title_tr and not self.title_en:
            raise ValidationError("En az bir dilde başlık girilmelidir (TR veya EN)")
        if not self.description_tr and not self.description_en:
            raise ValidationError("En az bir dilde açıklama girilmelidir (TR veya EN)")

    def get_photos(self):
        """Return list of available photos"""
        photos = []
        if self.photo1:
            photos.append(self.photo1)
        if self.photo2:
            photos.append(self.photo2)
        if self.photo3:
            photos.append(self.photo3)
        return photos

    def save(self, *args, **kwargs):
        """Override save to compress images before saving"""
        from django.conf import settings
        from .utils import compress_image

        if getattr(settings, 'IMAGE_COMPRESS_ENABLED', True):
            max_size = getattr(settings, 'IMAGE_MAX_SIZE', (1920, 1920))
            quality = getattr(settings, 'IMAGE_QUALITY', 85)

            if self.photo1 and not self.pk:
                self.photo1 = compress_image(self.photo1, max_size, quality)
            if self.photo2 and not self.pk:
                self.photo2 = compress_image(self.photo2, max_size, quality)
            if self.photo3 and not self.pk:
                self.photo3 = compress_image(self.photo3, max_size, quality)

        super().save(*args, **kwargs)
