from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile, Sector


class SignUpForm(UserCreationForm):
    """Custom signup form with additional fields"""
    
    # Personal information
    first_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ad',
            'data-i18n-placeholder': 'signup.first_name'
        }),
        label='Ad'
    )
    last_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Soyad',
            'data-i18n-placeholder': 'signup.last_name'
        }),
        label='Soyad'
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'E-posta Adresi',
            'data-i18n-placeholder': 'signup.email'
        }),
        label='E-posta'
    )
    
    # Company information
    company_name = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Firma Adı',
            'data-i18n-placeholder': 'signup.company_name'
        }),
        label='Firma Adı'
    )
    phone_number = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+90 555 123 4567',
            'data-i18n-placeholder': 'signup.phone_number'
        }),
        label='Telefon Numarası'
    )
    country = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ülke',
            'data-i18n-placeholder': 'signup.country'
        }),
        label='Ülke'
    )
    city = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Şehir',
            'data-i18n-placeholder': 'signup.city'
        }),
        label='Şehir'
    )
    
    # User type
    is_buyer = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'is_buyer'
        }),
        label='Alıcı'
    )
    is_producer = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'is_producer'
        }),
        label='Üretici'
    )
    
    # Buyer-specific fields
    buyer_interested_sectors = forms.ModelMultipleChoiceField(
        queryset=Sector.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control sector-select',
        }),
        label='İlgilenilen Sektörler'
    )
    buyer_quarterly_volume = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control buyer-field',
            'placeholder': '50000',
            'data-i18n-placeholder': 'signup.buyer_volume'
        }),
        label='Çeyreklik Alım Hacmi (USD)'
    )
    
    # Producer-specific fields
    producer_sectors = forms.ModelMultipleChoiceField(
        queryset=Sector.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control sector-select',
        }),
        label='Sektörler'
    )
    producer_quarterly_sales = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control producer-field',
            'placeholder': '100000',
            'data-i18n-placeholder': 'signup.producer_sales'
        }),
        label='Çeyreklik Satış Hacmi (USD)'
    )
    producer_product_count = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control producer-field',
            'placeholder': '50',
            'data-i18n-placeholder': 'signup.producer_products'
        }),
        label='Yaklaşık Ürün Sayısı'
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Kullanıcı Adı',
                'data-i18n-placeholder': 'signup.username'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Şifre',
            'data-i18n-placeholder': 'signup.password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Şifre Tekrar',
            'data-i18n-placeholder': 'signup.password_confirm'
        })
        # Set individual sector choice labels (will be dynamic via JS later)
        self.fields['buyer_interested_sectors'].label_from_instance = lambda obj: f"{obj.name_tr} | {obj.name_en}"
        self.fields['producer_sectors'].label_from_instance = lambda obj: f"{obj.name_tr} | {obj.name_en}"
    
    def clean(self):
        cleaned_data = super().clean()
        is_buyer = cleaned_data.get('is_buyer')
        is_producer = cleaned_data.get('is_producer')
        
        # At least one user type must be selected
        if not is_buyer and not is_producer:
            raise forms.ValidationError("Lütfen en az bir kullanıcı tipi seçin (Alıcı veya Üretici).")
        
        # Validate buyer fields if buyer is selected
        if is_buyer:
            if not cleaned_data.get('buyer_interested_sectors'):
                self.add_error('buyer_interested_sectors', 'Alıcı olarak kayıt oluyorsanız bu alan zorunludur.')
            if not cleaned_data.get('buyer_quarterly_volume'):
                self.add_error('buyer_quarterly_volume', 'Alıcı olarak kayıt oluyorsanız bu alan zorunludur.')
        
        # Validate producer fields if producer is selected
        if is_producer:
            if not cleaned_data.get('producer_sectors'):
                self.add_error('producer_sectors', 'Üretici olarak kayıt oluyorsanız bu alan zorunludur.')
            if not cleaned_data.get('producer_quarterly_sales'):
                self.add_error('producer_quarterly_sales', 'Üretici olarak kayıt oluyorsanız bu alan zorunludur.')
            if not cleaned_data.get('producer_product_count'):
                self.add_error('producer_product_count', 'Üretici olarak kayıt oluyorsanız bu alan zorunludur.')
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            
            # Create user profile
            profile = UserProfile.objects.create(
                user=user,
                company_name=self.cleaned_data['company_name'],
                phone_number=self.cleaned_data['phone_number'],
                country=self.cleaned_data['country'],
                city=self.cleaned_data['city'],
                is_buyer=self.cleaned_data['is_buyer'],
                is_producer=self.cleaned_data['is_producer'],
                buyer_quarterly_volume=self.cleaned_data.get('buyer_quarterly_volume'),
                producer_quarterly_sales=self.cleaned_data.get('producer_quarterly_sales'),
                producer_product_count=self.cleaned_data.get('producer_product_count')
            )
            
            # Add ManyToMany fields
            if self.cleaned_data.get('buyer_interested_sectors'):
                profile.buyer_interested_sectors.set(self.cleaned_data['buyer_interested_sectors'])
            if self.cleaned_data.get('producer_sectors'):
                profile.producer_sectors.set(self.cleaned_data['producer_sectors'])
        
        return user


class CustomLoginForm(AuthenticationForm):
    """Custom login form with styled widgets"""
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Kullanıcı Adı veya E-posta',
            'data-i18n-placeholder': 'login.username'
        }),
        label='Kullanıcı Adı'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Şifre',
            'data-i18n-placeholder': 'login.password'
        }),
        label='Şifre'
    )
