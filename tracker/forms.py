from django import forms
from .models import StationeryItem, Sale, SaleItem, Debt, Payment, Customer, Category


class StationeryItemForm(forms.ModelForm):
    class Meta:
        model = StationeryItem
        fields = ['name', 'description', 'category', 'sku', 'unit_price', 'cost_price', 
                 'stock_quantity', 'minimum_stock', 'supplier', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'unit_price': forms.NumberInput(attrs={'step': '0.01'}),
            'cost_price': forms.NumberInput(attrs={'step': '0.01'}),
        }


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone', 'address', 'is_active']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['customer', 'payment_method', 'is_paid', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class SaleItemForm(forms.ModelForm):
    class Meta:
        model = SaleItem
        fields = ['item', 'quantity', 'unit_price']
        widgets = {
            'unit_price': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'item': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'min': '1', 'class': 'form-control'}),
        }


class DebtForm(forms.ModelForm):
    class Meta:
        model = Debt
        fields = ['customer', 'sale', 'amount', 'due_date', 'description']
        widgets = {
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'payment_method', 'notes']
        widgets = {
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
