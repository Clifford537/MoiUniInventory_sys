from django import forms
from .models import Product, Transaction, Store
from django.core.exceptions import ValidationError
from django.db.models import Sum

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
        fields = ['product', 'transaction_type', 'quantity', 'remarks', 'broken_quantity']
        widgets = {
            'transaction_type': forms.Select(attrs={'onchange': 'toggleFields()'}),
            'broken_quantity': forms.NumberInput(attrs={'class': 'conditional-field'}),
        }

    def __init__(self, *args, **kwargs):
        super(TransactionForm, self).__init__(*args, **kwargs)
        self.fields['broken_quantity'].required = False

    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity')
        broken_quantity = cleaned_data.get('broken_quantity')
        transaction_type = cleaned_data.get('transaction_type')
        product = cleaned_data.get('product')

        if transaction_type == 'receive':
            if broken_quantity is None:
                broken_quantity = 0
            if broken_quantity > quantity:
                self.add_error('broken_quantity', 'Broken quantity cannot exceed the received quantity.')

            if product:
                issued_quantity = Transaction.objects.filter(
                    product=product,
                    transaction_type='issue'
                ).aggregate(
                    issued_quantity=Sum('quantity')
                )['issued_quantity'] or 0

                received_quantity = Transaction.objects.filter(
                    product=product,
                    transaction_type='receive'
                ).aggregate(
                    received_quantity=Sum('quantity')
                )['received_quantity'] or 0

                total_received = received_quantity + quantity

                if total_received > issued_quantity:
                    remaining = issued_quantity - received_quantity
                    self.add_error('quantity', f'Received quantity cannot exceed issued quantity. You can only receive up to {remaining} more.')

        elif transaction_type == 'issue':
            if product:
                if product.quantity < quantity:
                    self.add_error('quantity', f'Issued quantity exceeds available quantity. Available quantity is {product.quantity}.')

        return cleaned_data
