from django import forms
from django.forms import inlineformset_factory
from .models import Receipt, ReceiptItem, BusinessProfile

# Business Profile Form
class BusinessProfileForm(forms.ModelForm):
    class Meta:
        model = BusinessProfile
        fields = ['brand_name', 'email', 'phone_number', 'location']

# Receipt Form
class ReceiptForm(forms.ModelForm):
    class Meta:
        model = Receipt
        fields = ['customer_name']


class ReceiptItemForm(forms.ModelForm):
    class Meta:
        model = ReceiptItem
        fields = ['product_name', 'quantity', 'price', 'description']
        labels = {
            'product_name': 'Product Name',
            'quantity': 'Quantity',
            'price': 'Price (₦)',
            'description': 'Description (Optional)'
        }

# Receipt Items Formset
ReceiptItemFormSet = inlineformset_factory(
    Receipt,
    ReceiptItem,
    form=ReceiptItemForm,  # 👈 tell it to use your form
    extra=1,
    can_delete=True
)



from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)  # force email

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
