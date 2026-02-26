from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .models import UserProfile, Sector, SignupRequest, Product, ProductTag, ExpoSignup, ProfileEditRequest



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
    open_address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Sokak, Mahalle, Posta Kodu…',
            'data-i18n-placeholder': 'signup.open_address',
            'rows': 3,
        }),
        label='Açık Adres'
    )
    website = forms.URLField(
        max_length=255,
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://firmaniz.com',
            'data-i18n-placeholder': 'signup.website'
        }),
        label='Web Sitesi'
    )
    about_company = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Firmanız hakkında kısa bir açıklama…',
            'data-i18n-placeholder': 'signup.about_company',
            'rows': 4,
        }),
        label='Firma Hakkında'
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
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Kullanıcı Adı veya E-posta',
            'data-i18n-placeholder': 'login.username'
        }),
        label='Kullanıcı Adı veya E-posta'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Şifre',
            'data-i18n-placeholder': 'login.password'
        }),
        label='Şifre'
    )


class ProfileEditForm(forms.Form):
    """Form for users to edit their profile - creates edit request for admin approval"""
    
    # Personal information (username, email, first name, and last name cannot be changed)
    
    # Company information
    company_name = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Firma Adı'
        }),
        label='Firma Adı'
    )
    phone_number = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+90 555 123 4567'
        }),
        label='Telefon Numarası'
    )
    country = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ülke'
        }),
        label='Ülke'
    )
    city = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Şehir'
        }),
        label='Şehir'
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
            'placeholder': '50000'
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
            'placeholder': '100000'
        }),
        label='Çeyreklik Satış Hacmi (USD)'
    )
    producer_product_count = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control producer-field',
            'placeholder': '50'
        }),
        label='Yaklaşık Ürün Sayısı'
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set sector labels
        self.fields['buyer_interested_sectors'].label_from_instance = lambda obj: f"{obj.name_tr} | {obj.name_en}"
        self.fields['producer_sectors'].label_from_instance = lambda obj: f"{obj.name_tr} | {obj.name_en}"
        
        # Pre-populate fields with current user data if available
        if self.user and hasattr(self.user, 'profile'):
            profile = self.user.profile
            if not self.is_bound:  # Only set initial values if form is not bound
                self.fields['company_name'].initial = profile.company_name
                self.fields['phone_number'].initial = profile.phone_number
                self.fields['country'].initial = profile.country
                self.fields['city'].initial = profile.city
                
                if profile.is_buyer:
                    self.fields['buyer_interested_sectors'].initial = profile.buyer_interested_sectors.all()
                    self.fields['buyer_quarterly_volume'].initial = profile.buyer_quarterly_volume
                
                if profile.is_producer:
                    self.fields['producer_sectors'].initial = profile.producer_sectors.all()
                    self.fields['producer_quarterly_sales'].initial = profile.producer_quarterly_sales
                    self.fields['producer_product_count'].initial = profile.producer_product_count
    
    def clean(self):
        cleaned_data = super().clean()
        
        if not self.user or not hasattr(self.user, 'profile'):
            raise forms.ValidationError("Kullanıcı profili bulunamadı.")
        
        profile = self.user.profile
        
        # Validate buyer fields if user is a buyer
        if profile.is_buyer:
            if not cleaned_data.get('buyer_interested_sectors'):
                self.add_error('buyer_interested_sectors', 'Alıcı olarak bu alan zorunludur.')
            if not cleaned_data.get('buyer_quarterly_volume'):
                self.add_error('buyer_quarterly_volume', 'Alıcı olarak bu alan zorunludur.')
        
        # Validate producer fields if user is a producer
        if profile.is_producer:
            if not cleaned_data.get('producer_sectors'):
                self.add_error('producer_sectors', 'Üretici olarak bu alan zorunludur.')
            if not cleaned_data.get('producer_quarterly_sales'):
                self.add_error('producer_quarterly_sales', 'Üretici olarak bu alan zorunludur.')
            if not cleaned_data.get('producer_product_count'):
                self.add_error('producer_product_count', 'Üretici olarak bu alan zorunludur.')
        
        return cleaned_data
    
    def save(self, commit=True):
        """Create a profile edit request instead of updating profile directly"""
        from .models import ProfileEditRequest
        
        # Get sector IDs as comma-separated strings
        buyer_sector_ids = ','.join(
            str(s.id) for s in self.cleaned_data.get('buyer_interested_sectors', [])
        ) if self.cleaned_data.get('buyer_interested_sectors') else ''
        
        producer_sector_ids = ','.join(
            str(s.id) for s in self.cleaned_data.get('producer_sectors', [])
        ) if self.cleaned_data.get('producer_sectors') else ''
        
        if commit:
            # Create profile edit request
            # Note: first_name and last_name use current user values (not editable)
            edit_request = ProfileEditRequest.objects.create(
                user=self.user,
                first_name=self.user.first_name,
                last_name=self.user.last_name,
                company_name=self.cleaned_data['company_name'],
                phone_number=self.cleaned_data['phone_number'],
                country=self.cleaned_data['country'],
                city=self.cleaned_data['city'],
                buyer_interested_sectors_ids=buyer_sector_ids,
                buyer_quarterly_volume=self.cleaned_data.get('buyer_quarterly_volume'),
                producer_sectors_ids=producer_sector_ids,
                producer_quarterly_sales=self.cleaned_data.get('producer_quarterly_sales'),
                producer_product_count=self.cleaned_data.get('producer_product_count'),
                status='pending'
            )
            return edit_request
        
        return None


class ProductForm(forms.ModelForm):
    """Form for producers to add/edit products"""
    
    sector = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Sektör'
    )
    
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
        fields = ['sector', 'title_tr', 'title_en', 'description_tr', 'description_en', 
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
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter sectors based on user's profile
        if user and hasattr(user, 'profile'):
            self.fields['sector'].queryset = user.profile.producer_sectors.all()
        else:
            # Fallback to all sectors if no user provided
            from .models import Sector
            self.fields['sector'].queryset = Sector.objects.all()
        
        # Set sector labels
        self.fields['sector'].label_from_instance = lambda obj: f"{obj.name_tr} | {obj.name_en}"
        
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


class ExpoSignupForm(forms.ModelForm):
    """Form for users to sign up for expos"""
    
    product_count = forms.IntegerField(
        min_value=1,
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Kaç ürün sergilemek istiyorsunuz?'
        }),
        label='Ürün Sayısı'
    )
    
    uses_listed_products = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'uses_listed_products'
        }),
        label='Made in İzmir\'de listelenen ürünlerimden seçmek istiyorum'
    )
    
    selected_products = forms.ModelMultipleChoiceField(
        queryset=None,  # Will be set in __init__
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control',
            'id': 'selected_products'
        }),
        label='Ürünlerinizi Seçin'
    )
    
    product_description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Fuarda sergilemek istediğiniz ürünleri açıklayın...',
            'rows': 4,
            'id': 'product_description'
        }),
        label='Ürün Açıklaması'
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Ek notlarınız varsa buraya yazabilirsiniz...',
            'rows': 3
        }),
        label='Notlar (İsteğe Bağlı)'
    )
    
    class Meta:
        model = ExpoSignup
        fields = ['product_count', 'uses_listed_products', 'selected_products', 'product_description', 'notes']
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter products to only show user's own products
        if user:
            self.fields['selected_products'].queryset = Product.objects.filter(
                producer=user,
                is_active=True
            )
        else:
            self.fields['selected_products'].queryset = Product.objects.none()
        
        # Set product labels
        self.fields['selected_products'].label_from_instance = lambda obj: obj.title_tr or obj.title_en
    
    def clean(self):
        cleaned_data = super().clean()
        uses_listed_products = cleaned_data.get('uses_listed_products')
        selected_products = cleaned_data.get('selected_products')
        product_description = cleaned_data.get('product_description')
        
        # If uses_listed_products is checked, selected_products is required
        if uses_listed_products:
            if not selected_products or selected_products.count() == 0:
                self.add_error('selected_products', 'Lütfen en az bir ürün seçin.')
        else:
            # If not using listed products, product_description is required
            if not product_description or not product_description.strip():
                self.add_error('product_description', 'Lütfen ürün açıklaması girin.')
        
        return cleaned_data
