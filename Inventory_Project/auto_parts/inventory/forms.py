from django import forms
from .models import Sale,Product,Invoice,Customer

# forms.py
from django import forms
from .models import Sale, Product

from django import forms

class CreateSaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = [
            'customer', 'phone', 'product', 'quantity_sold',
            'unit_price', 'gst', 'discount', 'cash_received', 'status'
        ]
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity_sold': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'gst': forms.NumberInput(attrs={'class': 'form-control'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control'}),
            'cash_received': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }



class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name','quantity', 'price', 'reorder_level']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'required': True,
                'placeholder': 'Enter price in ₹'
            }),
              'reorder_level': forms.NumberInput(attrs={
              'class': 'form-control',
            'style': 'width: 120px; height: 38px; border-radius: 6px;',
            'placeholder': 'e.g. 10'}),

        }

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            'customer_name', 'customer_phone',
            'override_product_name', 'override_unit_price', 'override_quantity',
            'discount', 'gst', 'cash_received', 'override_balance_due', 'status'
        ]
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'override_product_name': forms.TextInput(attrs={'class': 'form-control'}),
            'override_unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'override_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'gst': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'cash_received': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'override_balance_due': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }



