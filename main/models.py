from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


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
    
    def __str__(self):
        return f"{self.username} - {self.company_name} ({self.get_status_display()})"
    
    def get_buyer_sectors(self):
        """Get buyer interested sectors as queryset"""
        if self.buyer_interested_sectors_ids:
            ids = [int(id.strip()) for id in self.buyer_interested_sectors_ids.split(',') if id.strip()]
            return Sector.objects.filter(id__in=ids)
        return Sector.objects.none()
    
    def get_producer_sectors(self):
        """Get producer sectors as queryset"""
        if self.producer_sectors_ids:
            ids = [int(id.strip()) for id in self.producer_sectors_ids.split(',') if id.strip()]
            return Sector.objects.filter(id__in=ids)
        return Sector.objects.none()


class Sector(models.Model):
    """Sectors list for categorizing buyers and producers"""
    name_tr = models.CharField(max_length=200, verbose_name="Sektör Adı (TR)")
    name_en = models.CharField(max_length=200, verbose_name="Sektör Adı (EN)")

    class Meta:
        verbose_name = "Sektör"
        verbose_name_plural = "Sektörler"
        ordering = ['name_tr']

    def __str__(self):
        return self.name_tr


class UserProfile(models.Model):
    """Extended user profile for buyers and producers"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Common fields
    company_name = models.CharField(max_length=200, verbose_name="Firma Adı")
    phone_number = models.CharField(max_length=20, verbose_name="Telefon Numarası")
    country = models.CharField(max_length=100, verbose_name="Ülke")
    city = models.CharField(max_length=100, verbose_name="Şehir")
    
    # User type (can be both)
    is_buyer = models.BooleanField(default=False, verbose_name="Alıcı")
    is_producer = models.BooleanField(default=False, verbose_name="Üretici")
    
    # Buyer-specific fields
    buyer_interested_sectors = models.ManyToManyField(
        Sector,
        blank=True,
        related_name='interested_buyers',
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
        Sector,
        blank=True,
        related_name='producers',
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
        verbose_name = "Kullanıcı Profili"
        verbose_name_plural = "Kullanıcı Profilleri"
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.company_name}"
    
    def get_user_types(self):
        """Return user types as a list"""
        types = []
        if self.is_buyer:
            types.append("Alıcı")
        if self.is_producer:
            types.append("Üretici")
        return ", ".join(types) if types else "Belirtilmemiş"
