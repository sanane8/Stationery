from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import StationeryItem, Sale, SaleItem, Debt, Payment, Customer, Category
from .models import Expenditure


class StationeryItemForm(forms.ModelForm):
    class Meta:
        model = StationeryItem
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'sku': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'supplier': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'cost_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'minimum_stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['customer', 'payment_method', 'is_paid', 'notes']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'is_paid': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional notes...'}),
        }

class SaleItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default quantity to 1 for new forms
        if not self.instance.pk:
            self.fields['quantity'].initial = 1
    
    class Meta:
        model = SaleItem
        fields = ['item', 'quantity', 'unit_price']
        widgets = {
            'item': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class DebtForm(forms.ModelForm):
    unit_prices = {}
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate unit prices for JavaScript
        self.unit_prices = {
            str(item.pk): str(item.unit_price) 
            for item in StationeryItem.objects.filter(is_active=True)
        }
    
    class Meta:
        model = Debt
        fields = ['customer', 'sale', 'item', 'quantity', 'amount', 'due_date', 'description']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'sale': forms.Select(attrs={'class': 'form-control'}),
            'item': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class PaymentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.debt = kwargs.pop('debt', None)
        super().__init__(*args, **kwargs)
        
        # Set max amount attribute for client-side validation
        if self.debt:
            self.fields['amount'].widget.attrs.update({
                'max': self.debt.remaining_amount,
                'data-remaining': self.debt.remaining_amount
            })
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if self.debt and amount > self.debt.remaining_amount:
            raise forms.ValidationError(
                f'Payment amount cannot exceed the remaining debt amount of TZS {self.debt.remaining_amount:,.0f}'
            )
        return amount
    
    class Meta:
        model = Payment
        fields = ['amount', 'payment_method', 'notes']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ExpenditureForm(forms.ModelForm):
    class Meta:
        model = Expenditure
        fields = ['description', 'amount', 'category']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        
        # Add help text placeholders
        self.fields['username'].help_text = 'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'
        self.fields['password1'].help_text = 'Your password must contain at least 8 characters.'
        self.fields['password2'].help_text = 'Enter the same password as before, for verification.'
