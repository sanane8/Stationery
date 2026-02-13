from django.contrib import admin
from .models import Category, StationeryItem, Customer, Sale, SaleItem, Debt, Payment
from .models import Expenditure


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at']


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1


@admin.register(StationeryItem)
class StationeryItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'unit_price', 'cost_price', 'stock_quantity']
    list_filter = ['category']
    search_fields = ['name', 'supplier']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'email', 'phone']


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'sale_date', 'total_amount', 'payment_method']
    list_filter = ['payment_method', 'sale_date']
    search_fields = ['customer__name', 'notes']
    inlines = [SaleItemInline]


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ['sale', 'item', 'quantity', 'unit_price', 'total_price']
    list_filter = ['sale__sale_date']


@admin.register(Debt)
class DebtAdmin(admin.ModelAdmin):
    list_display = ['customer', 'amount', 'due_date', 'created_at']
    list_filter = ['due_date', 'created_at']
    search_fields = ['customer__name', 'description']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['debt', 'amount', 'payment_date', 'payment_method']
    list_filter = ['payment_method', 'payment_date']
    search_fields = ['debt__customer__name', 'notes']


@admin.register(Expenditure)
class ExpenditureAdmin(admin.ModelAdmin):
    list_display = ['id', 'category', 'amount', 'expense_date']
    list_filter = ['category', 'expense_date']
    search_fields = ['description']
    readonly_fields = ['created_at']
