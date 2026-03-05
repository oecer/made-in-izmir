from django import forms
from .models import ExpoSignup


class ExpoSignupForm(forms.ModelForm):
    """Form for users to sign up for expos"""

    product_count = forms.IntegerField(
        min_value=1, required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Kaç ürün sergilemek istiyorsunuz?'}),
        label='Ürün Sayısı'
    )

    uses_listed_products = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'uses_listed_products'}),
        label="Made in İzmir'de listelenen ürünlerimden seçmek istiyorum"
    )

    selected_products = forms.ModelMultipleChoiceField(
        queryset=None,  # Set in __init__
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'id': 'selected_products'}),
        label='Ürünlerinizi Seçin'
    )

    product_description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Fuarda sergilemek istediğiniz ürünleri açıklayın...', 'rows': 4, 'id': 'product_description'}),
        label='Ürün Açıklaması'
    )

    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Ek notlarınız varsa buraya yazabilirsiniz...', 'rows': 3}),
        label='Notlar (İsteğe Bağlı)'
    )

    class Meta:
        model = ExpoSignup
        fields = ['product_count', 'uses_listed_products', 'selected_products', 'product_description', 'notes']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        from catalog.models import Product
        if user and hasattr(user, 'profile') and user.profile.tenant:
            self.fields['selected_products'].queryset = Product.objects.filter(
                tenant=user.profile.tenant,
                is_active=True
            )
        else:
            self.fields['selected_products'].queryset = Product.objects.none()

        self.fields['selected_products'].label_from_instance = lambda obj: obj.title_tr or obj.title_en

    def clean(self):
        cleaned_data = super().clean()
        uses_listed_products = cleaned_data.get('uses_listed_products')
        selected_products = cleaned_data.get('selected_products')
        product_description = cleaned_data.get('product_description')

        if uses_listed_products:
            if not selected_products or selected_products.count() == 0:
                self.add_error('selected_products', 'Lütfen en az bir ürün seçin.')
        else:
            if not product_description or not product_description.strip():
                self.add_error('product_description', 'Lütfen ürün açıklaması girin.')

        return cleaned_data
