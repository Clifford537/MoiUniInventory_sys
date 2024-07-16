from django import forms
from .models import Product, Transaction, Store

class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['name', 'location', 'remarks']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['store', 'item_name', 'item_description', 'unit_price', 'quantity', 'remarks']

class TransactionForm(forms.ModelForm):
    TRANSACTION_CHOICES = (
        ('issue', 'Issue'),
        ('receive', 'Receive')
    )

    transaction_type = forms.ChoiceField(choices=TRANSACTION_CHOICES, label='Transaction Type')

    class Meta:
        model = Transaction
        fields = ['product', 'transaction_type', 'quantity', 'remarks']
