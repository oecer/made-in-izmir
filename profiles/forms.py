from django import forms
from accounts.models import TenantLogoRequest, TenantPhotoRequest


class TenantLogoRequestForm(forms.ModelForm):
    class Meta:
        model = TenantLogoRequest
        fields = ['logo']
        widgets = {
            'logo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def clean_logo(self):
        logo = self.cleaned_data.get('logo')
        if logo and hasattr(logo, 'size') and logo.size > 2 * 1024 * 1024:
            raise forms.ValidationError("Dosya boyutu 2MB'dan küçük olmalıdır.")
        return logo


class TenantPhotoRequestForm(forms.ModelForm):
    class Meta:
        model = TenantPhotoRequest
        fields = ['photo', 'caption_tr', 'caption_en']
        widgets = {
            'photo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'caption_tr': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Fotoğraf açıklaması (isteğe bağlı)'}),
            'caption_en': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Photo caption (optional)'}),
        }

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo and hasattr(photo, 'size') and photo.size > 10 * 1024 * 1024:
            raise forms.ValidationError("Dosya boyutu 10MB'dan küçük olmalıdır.")
        return photo
