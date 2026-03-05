from django import forms
from .models import Product, ProductTag


class ProductForm(forms.ModelForm):
    """Form for producers to add/edit products"""

    sector = forms.ModelChoiceField(
        queryset=None,  # Set in __init__
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Sektör'
    )

    tags = forms.ModelMultipleChoiceField(
        queryset=ProductTag.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        label='Etiketler (Maksimum 3)'
    )

    class Meta:
        model = Product
        fields = ['sector', 'title_tr', 'title_en', 'description_tr', 'description_en',
                  'photo1', 'photo2', 'photo3', 'tags', 'is_active']
        widgets = {
            'title_tr': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ürün Başlığı (Türkçe)', 'data-i18n': 'dashboard.title_tr'}),
            'title_en': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Title (English)', 'data-i18n': 'dashboard.title_en'}),
            'description_tr': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Ürün Açıklaması (Türkçe)', 'rows': 4, 'data-i18n': 'dashboard.desc_tr'}),
            'description_en': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Product Description (English)', 'rows': 4, 'data-i18n': 'dashboard.desc_en'}),
            'photo1': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'photo2': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'photo3': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'title_tr': 'Ürün Başlığı (Türkçe)',
            'title_en': 'Ürün Başlığı (İngilizce)',
            'description_tr': 'Ürün Açıklaması (Türkçe)',
            'description_en': 'Ürün Açıklaması (İngilizce)',
            'photo1': 'Fotoğraf 1',
            'photo2': 'Fotoğraf 2',
            'photo3': 'Fotoğraf 3',
            'is_active': 'Aktif',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user and hasattr(user, 'profile') and user.profile.tenant:
            self.fields['sector'].queryset = user.profile.tenant.producer_sectors.all()
        else:
            from .models import Sector
            self.fields['sector'].queryset = Sector.objects.all()

        self.fields['sector'].label_from_instance = lambda obj: f"{obj.name_tr} | {obj.name_en}"
        self.fields['tags'].label_from_instance = lambda obj: f"{obj.name_tr} | {obj.name_en}"

    def clean(self):
        cleaned_data = super().clean()

        if not cleaned_data.get('title_tr') and not cleaned_data.get('title_en'):
            raise forms.ValidationError("En az bir dilde başlık girilmelidir (Türkçe veya İngilizce)")

        if not cleaned_data.get('description_tr') and not cleaned_data.get('description_en'):
            raise forms.ValidationError("En az bir dilde açıklama girilmelidir (Türkçe veya İngilizce)")

        tags = cleaned_data.get('tags')
        if tags and tags.count() > 3:
            raise forms.ValidationError("Maksimum 3 etiket seçebilirsiniz")

        return cleaned_data
