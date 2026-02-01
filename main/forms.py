from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .models import UserProfile, Sector, SignupRequest, Product, ProductTag



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
        """Create a signup request instead of creating user directly"""
        # Don't create the user yet - just create a signup request
        
        # Get sector IDs as comma-separated strings
        buyer_sector_ids = ','.join(
            str(s.id) for s in self.cleaned_data.get('buyer_interested_sectors', [])
        ) if self.cleaned_data.get('buyer_interested_sectors') else ''
        
        producer_sector_ids = ','.join(
            str(s.id) for s in self.cleaned_data.get('producer_sectors', [])
        ) if self.cleaned_data.get('producer_sectors') else ''
        
        if commit:
            # Create signup request
            signup_request = SignupRequest.objects.create(
                username=self.cleaned_data['username'],
                email=self.cleaned_data['email'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                password_hash=make_password(self.cleaned_data['password1']),
                company_name=self.cleaned_data['company_name'],
                phone_number=self.cleaned_data['phone_number'],
                country=self.cleaned_data['country'],
                city=self.cleaned_data['city'],
                is_buyer=self.cleaned_data['is_buyer'],
                is_producer=self.cleaned_data['is_producer'],
                buyer_interested_sectors_ids=buyer_sector_ids,
                buyer_quarterly_volume=self.cleaned_data.get('buyer_quarterly_volume'),
                producer_sectors_ids=producer_sector_ids,
                producer_quarterly_sales=self.cleaned_data.get('producer_quarterly_sales'),
                producer_product_count=self.cleaned_data.get('producer_product_count'),
                status='pending'
            )
            return signup_request
        
        return None



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


class ProductForm(forms.ModelForm):
    """Form for producers to add/edit products"""
    
    tags = forms.ModelMultipleChoiceField(
        queryset=ProductTag.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control'
        }),
        label='Etiketler (Maksimum 3)'
    )
    
    class Meta:
        model = Product
        fields = ['title_tr', 'title_en', 'description_tr', 'description_en', 
                  'photo1', 'photo2', 'photo3', 'tags', 'is_active']
        widgets = {
            'title_tr': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ürün Başlığı (Türkçe)',
                'data-i18n': 'dashboard.title_tr'
            }),
            'title_en': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Product Title (English)',
                'data-i18n': 'dashboard.title_en'
            }),
            'description_tr': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Ürün Açıklaması (Türkçe)',
                'rows': 4,
                'data-i18n': 'dashboard.desc_tr'
            }),
            'description_en': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Product Description (English)',
                'rows': 4,
                'data-i18n': 'dashboard.desc_en'
            }),
            'photo1': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'photo2': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'photo3': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'title_tr': 'Ürün Başlığı (Türkçe)',
            'title_en': 'Ürün Başlığı (İngilizce)',
            'description_tr': 'Ürün Açıklaması (Türkçe)',
            'description_en': 'Ürün Açıklaması (İngilizce)',
            'photo1': 'Fotoğraf 1',
            'photo2': 'Fotoğraf 2',
            'photo3': 'Fotoğraf 3',
            'is_active': 'Aktif'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set tag labels
        self.fields['tags'].label_from_instance = lambda obj: f"{obj.name_tr} | {obj.name_en}"
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validate that at least one title is provided
        if not cleaned_data.get('title_tr') and not cleaned_data.get('title_en'):
            raise forms.ValidationError("En az bir dilde başlık girilmelidir (Türkçe veya İngilizce)")
        
        # Validate that at least one description is provided
        if not cleaned_data.get('description_tr') and not cleaned_data.get('description_en'):
            raise forms.ValidationError("En az bir dilde açıklama girilmelidir (Türkçe veya İngilizce)")
        
        # Validate max 3 tags
        tags = cleaned_data.get('tags')
        if tags and tags.count() > 3:
            raise forms.ValidationError("Maksimum 3 etiket seçebilirsiniz")
        
        return cleaned_data
