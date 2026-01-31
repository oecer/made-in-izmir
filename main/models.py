from django.db import models
from django.contrib.auth.models import User


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
    buyer_interested_sectors = models.TextField(
        blank=True, 
        null=True,
        verbose_name="İlgilenilen Sektörler",
        help_text="Virgülle ayrılmış sektörler"
    )
    buyer_quarterly_volume = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        blank=True, 
        null=True,
        verbose_name="Çeyreklik Alım Hacmi (USD)"
    )
    
    # Producer-specific fields
    producer_sector = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        verbose_name="Sektör"
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
