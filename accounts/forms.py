import unicodedata
import re

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .models import SignupRequest, ProfileEditRequest


def _slugify_name(value):
    """Normalize a name part to lowercase ASCII letters only."""
    value = unicodedata.normalize('NFKD', value)
    value = value.encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^a-z]', '', value.lower())
    return value or 'user'


def generate_unique_username(first_name, last_name):
    """Generate username as firstname.lastname, append 1/2/3... if taken."""
    base = f"{_slugify_name(first_name)}.{_slugify_name(last_name)}"
    candidate = base
    counter = 1
    existing_users = set(User.objects.values_list('username', flat=True))
    existing_requests = set(SignupRequest.objects.values_list('username', flat=True))
    taken = existing_users | existing_requests
    while candidate in taken:
        candidate = f"{base}{counter}"
        counter += 1
    return candidate


class SignUpForm(UserCreationForm):
    """Custom signup form with additional fields"""

    # Personal information
    first_name = forms.CharField(
        max_length=100, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ad', 'data-i18n-placeholder': 'signup.first_name'}),
        label='Ad'
    )
    last_name = forms.CharField(
        max_length=100, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Soyad', 'data-i18n-placeholder': 'signup.last_name'}),
        label='Soyad'
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'E-posta Adresi', 'data-i18n-placeholder': 'signup.email'}),
        label='E-posta'
    )

    # Company information
    company_name = forms.CharField(
        max_length=200, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Firma Adı', 'data-i18n-placeholder': 'signup.company_name'}),
        label='Firma Adı'
    )
    phone_number = forms.CharField(
        max_length=20, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+90 555 123 4567', 'data-i18n-placeholder': 'signup.phone_number'}),
        label='Telefon Numarası'
    )
    country = forms.CharField(
        max_length=100, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ülke', 'data-i18n-placeholder': 'signup.country'}),
        label='Ülke'
    )
    city = forms.CharField(
        max_length=100, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Şehir', 'data-i18n-placeholder': 'signup.city'}),
        label='Şehir'
    )
    open_address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Sokak, Mahalle, Posta Kodu…', 'data-i18n-placeholder': 'signup.open_address', 'rows': 3}),
        label='Açık Adres'
    )
    website = forms.URLField(
        max_length=255, required=False,
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://firmaniz.com', 'data-i18n-placeholder': 'signup.website'}),
        label='Web Sitesi'
    )
    about_company = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Firmanız hakkında kısa bir açıklama…', 'data-i18n-placeholder': 'signup.about_company', 'rows': 4}),
        label='Firma Hakkında'
    )

    # User type
    is_buyer = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'is_buyer'}),
        label='Alıcı'
    )
    is_producer = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'is_producer'}),
        label='Üretici'
    )

    # Buyer-specific fields
    buyer_interested_sectors = forms.ModelMultipleChoiceField(
        queryset=None,  # Set in __init__
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control sector-select'}),
        label='İlgilenilen Sektörler'
    )
    buyer_quarterly_volume = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control buyer-field', 'placeholder': '50000', 'data-i18n-placeholder': 'signup.buyer_volume'}),
        label='Çeyreklik Alım Hacmi (USD)'
    )

    # Producer-specific fields
    producer_sectors = forms.ModelMultipleChoiceField(
        queryset=None,  # Set in __init__
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control sector-select'}),
        label='Sektörler'
    )
    producer_quarterly_sales = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control producer-field', 'placeholder': '100000', 'data-i18n-placeholder': 'signup.producer_sales'}),
        label='Çeyreklik Satış Hacmi (USD)'
    )
    producer_product_count = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control producer-field', 'placeholder': '50', 'data-i18n-placeholder': 'signup.producer_products'}),
        label='Yaklaşık Ürün Sayısı'
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Username is auto-generated; remove it from the rendered form
        self.fields.pop('username', None)
        from catalog.models import Sector
        self.fields['buyer_interested_sectors'].queryset = Sector.objects.all()
        self.fields['producer_sectors'].queryset = Sector.objects.all()
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Şifre', 'data-i18n-placeholder': 'signup.password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Şifre Tekrar', 'data-i18n-placeholder': 'signup.password_confirm'})
        self.fields['buyer_interested_sectors'].label_from_instance = lambda obj: f"{obj.name_tr} | {obj.name_en}"
        self.fields['producer_sectors'].label_from_instance = lambda obj: f"{obj.name_tr} | {obj.name_en}"

    def clean_username(self):
        # Username is auto-generated; skip parent validation
        return self.cleaned_data.get('username', '')

    def clean(self):
        cleaned_data = super().clean()
        is_buyer = cleaned_data.get('is_buyer')
        is_producer = cleaned_data.get('is_producer')

        if not is_buyer and not is_producer:
            raise forms.ValidationError("Lütfen en az bir kullanıcı tipi seçin (Alıcı veya Üretici).")

        if is_buyer:
            if not cleaned_data.get('buyer_interested_sectors'):
                self.add_error('buyer_interested_sectors', 'Alıcı olarak kayıt oluyorsanız bu alan zorunludur.')
            if not cleaned_data.get('buyer_quarterly_volume'):
                self.add_error('buyer_quarterly_volume', 'Alıcı olarak kayıt oluyorsanız bu alan zorunludur.')

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
        buyer_sector_ids = ','.join(
            str(s.id) for s in self.cleaned_data.get('buyer_interested_sectors', [])
        ) if self.cleaned_data.get('buyer_interested_sectors') else ''

        producer_sector_ids = ','.join(
            str(s.id) for s in self.cleaned_data.get('producer_sectors', [])
        ) if self.cleaned_data.get('producer_sectors') else ''

        if commit:
            username = generate_unique_username(
                self.cleaned_data['first_name'],
                self.cleaned_data['last_name'],
            )
            signup_request = SignupRequest.objects.create(
                username=username,
                email=self.cleaned_data['email'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                password_hash=make_password(self.cleaned_data['password1']),
                company_name=self.cleaned_data['company_name'],
                phone_number=self.cleaned_data['phone_number'],
                country=self.cleaned_data['country'],
                city=self.cleaned_data['city'],
                open_address=self.cleaned_data.get('open_address') or '',
                website=self.cleaned_data.get('website') or '',
                about_company=self.cleaned_data.get('about_company') or '',
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
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Kullanıcı Adı veya E-posta', 'data-i18n-placeholder': 'login.username'}),
        label='Kullanıcı Adı veya E-posta'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Şifre', 'data-i18n-placeholder': 'login.password'}),
        label='Şifre'
    )


class ProfileEditForm(forms.Form):
    """Form for users to edit their profile - creates edit request for admin approval"""

    company_name = forms.CharField(
        max_length=200, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Firma Adı'}),
        label='Firma Adı'
    )
    phone_number = forms.CharField(
        max_length=20, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+90 555 123 4567'}),
        label='Telefon Numarası'
    )
    country = forms.CharField(
        max_length=100, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ülke'}),
        label='Ülke'
    )
    city = forms.CharField(
        max_length=100, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Şehir'}),
        label='Şehir'
    )
    open_address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Sokak, Mahalle, Posta Kodu…', 'rows': 3}),
        label='Açık Adres'
    )

    buyer_interested_sectors = forms.ModelMultipleChoiceField(
        queryset=None,  # Set in __init__
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control sector-select'}),
        label='İlgilenilen Sektörler'
    )
    buyer_quarterly_volume = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control buyer-field', 'placeholder': '50000'}),
        label='Çeyreklik Alım Hacmi (USD)'
    )

    producer_sectors = forms.ModelMultipleChoiceField(
        queryset=None,  # Set in __init__
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control sector-select'}),
        label='Sektörler'
    )
    producer_quarterly_sales = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control producer-field', 'placeholder': '100000'}),
        label='Çeyreklik Satış Hacmi (USD)'
    )
    producer_product_count = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control producer-field', 'placeholder': '50'}),
        label='Yaklaşık Ürün Sayısı'
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        from catalog.models import Sector
        self.fields['buyer_interested_sectors'].queryset = Sector.objects.all()
        self.fields['producer_sectors'].queryset = Sector.objects.all()
        self.fields['buyer_interested_sectors'].label_from_instance = lambda obj: f"{obj.name_tr} | {obj.name_en}"
        self.fields['producer_sectors'].label_from_instance = lambda obj: f"{obj.name_tr} | {obj.name_en}"

        if self.user and hasattr(self.user, 'profile') and self.user.profile.tenant:
            tenant = self.user.profile.tenant
            if not self.is_bound:
                self.fields['company_name'].initial = tenant.company_name
                self.fields['phone_number'].initial = tenant.phone_number
                self.fields['country'].initial = tenant.country
                self.fields['city'].initial = tenant.city
                self.fields['open_address'].initial = tenant.open_address
                if tenant.is_buyer:
                    self.fields['buyer_interested_sectors'].initial = tenant.buyer_interested_sectors.all()
                    self.fields['buyer_quarterly_volume'].initial = tenant.buyer_quarterly_volume
                if tenant.is_producer:
                    self.fields['producer_sectors'].initial = tenant.producer_sectors.all()
                    self.fields['producer_quarterly_sales'].initial = tenant.producer_quarterly_sales
                    self.fields['producer_product_count'].initial = tenant.producer_product_count

    def clean(self):
        cleaned_data = super().clean()

        if not self.user or not hasattr(self.user, 'profile') or not self.user.profile.tenant:
            raise forms.ValidationError("Kullanıcı profili bulunamadı.")

        tenant = self.user.profile.tenant

        if tenant.is_buyer:
            if not cleaned_data.get('buyer_interested_sectors'):
                self.add_error('buyer_interested_sectors', 'Alıcı olarak bu alan zorunludur.')
            if not cleaned_data.get('buyer_quarterly_volume'):
                self.add_error('buyer_quarterly_volume', 'Alıcı olarak bu alan zorunludur.')

        if tenant.is_producer:
            if not cleaned_data.get('producer_sectors'):
                self.add_error('producer_sectors', 'Üretici olarak bu alan zorunludur.')
            if not cleaned_data.get('producer_quarterly_sales'):
                self.add_error('producer_quarterly_sales', 'Üretici olarak bu alan zorunludur.')
            if not cleaned_data.get('producer_product_count'):
                self.add_error('producer_product_count', 'Üretici olarak bu alan zorunludur.')

        return cleaned_data

    def save(self, commit=True):
        """Create a profile edit request instead of updating profile directly"""
        buyer_sector_ids = ','.join(
            str(s.id) for s in self.cleaned_data.get('buyer_interested_sectors', [])
        ) if self.cleaned_data.get('buyer_interested_sectors') else ''

        producer_sector_ids = ','.join(
            str(s.id) for s in self.cleaned_data.get('producer_sectors', [])
        ) if self.cleaned_data.get('producer_sectors') else ''

        if commit:
            edit_request = ProfileEditRequest.objects.create(
                user=self.user,
                first_name=self.user.first_name,
                last_name=self.user.last_name,
                company_name=self.cleaned_data['company_name'],
                phone_number=self.cleaned_data['phone_number'],
                country=self.cleaned_data['country'],
                city=self.cleaned_data['city'],
                open_address=self.cleaned_data.get('open_address') or '',
                buyer_interested_sectors_ids=buyer_sector_ids,
                buyer_quarterly_volume=self.cleaned_data.get('buyer_quarterly_volume'),
                producer_sectors_ids=producer_sector_ids,
                producer_quarterly_sales=self.cleaned_data.get('producer_quarterly_sales'),
                producer_product_count=self.cleaned_data.get('producer_product_count'),
                status='pending'
            )
            return edit_request

        return None
