"""
Django admin configuration for stationery_tracker with enhanced visual design.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.utils.html import format_html
from django.urls import reverse
from django.templatetags.static import static
from .models import (
    Category, Product, Customer, Supplier, StationeryItem, 
    Sale, SaleItem, Debt, Expenditure
)

# Register your models here with enhanced admin configuration


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)
    ordering = ('name',)
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description'),
            'classes': ('wide',),
        }),
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'unit_price', 'stock_quantity', 'created_at')
    search_fields = ('name', 'description', 'category__name')
    list_filter = ('category', 'created_at')
    ordering = ('name',)
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'category', 'unit_price', 'stock_quantity'),
            'classes': ('wide',),
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('category')


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'created_at')
    search_fields = ('name', 'phone', 'email')
    list_filter = ('created_at',)
    ordering = ('name',)
    
    fieldsets = (
        (None, {
            'fields': ('name', 'phone', 'email', 'address'),
            'classes': ('wide',),
        }),
    )


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'created_at')
    search_fields = ('name', 'phone', 'email')
    list_filter = ('created_at',)
    ordering = ('name',)
    
    fieldsets = (
        (None, {
            'fields': ('name', 'phone', 'email', 'address'),
            'classes': ('wide',),
        }),
    )


@admin.register(StationeryItem)
class StationeryItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'supplier', 'unit_price', 'stock_quantity', 'created_at')
    search_fields = ('name', 'description', 'category__name', 'supplier__name')
    list_filter = ('category', 'supplier', 'created_at')
    ordering = ('name',)
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'category', 'supplier', 'unit_price', 'stock_quantity'),
            'classes': ('wide',),
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('category', 'supplier')


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1
    min_num = 0
    fields = ('product', 'quantity', 'unit_price', 'total_price')
    readonly_fields = ('unit_price', 'total_price')
    
    def total_price(self, obj):
        return obj.quantity * obj.unit_price if obj.quantity and obj.unit_price else 0


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'date', 'total_amount', 'payment_method', 'created_at')
    search_fields = ('customer__name', 'payment_method')
    list_filter = ('date', 'payment_method', 'customer')
    ordering = ('-date',)
    date_hierarchy = 'date'
    
    fieldsets = (
        (None, {
            'fields': ('customer', 'date', 'payment_method'),
            'classes': ('wide',),
        }),
        ('Sale Items', {
            'fields': ('saleitem_set',),
            'classes': ('collapse',),
        }),
    )
    
    inlines = [SaleItemInline]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('customer')


@admin.register(Debt)
class DebtAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'amount', 'due_date', 'created_at', 'is_paid')
    search_fields = ('customer__name',)
    list_filter = ('due_date', 'is_paid', 'customer')
    ordering = ('due_date',)
    date_hierarchy = 'due_date'
    
    fieldsets = (
        (None, {
            'fields': ('customer', 'amount', 'due_date', 'is_paid'),
            'classes': ('wide',),
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('customer')


@admin.register(Expenditure)
class ExpenditureAdmin(admin.ModelAdmin):
    list_display = ('id', 'description', 'amount', 'date', 'created_at')
    search_fields = ('description',)
    list_filter = ('date',)
    ordering = ('-date',)
    date_hierarchy = 'date'
    
    fieldsets = (
        (None, {
            'fields': ('description', 'amount', 'date'),
            'classes': ('wide',),
        }),
    )


# Enhanced User Admin
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    ordering = ('username',)
    
    fieldsets = (
        (None, {
            'fields': ('username', 'password'),
            'classes': ('wide',),
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email'),
            'classes': ('wide',),
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',),
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',),
        }),
    )
    
    add_fieldsets = (
        (None, {
            'fields': ('username', 'password1', 'password2'),
            'classes': ('wide',),
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email'),
            'classes': ('wide',),
        }),
    )


# Replace default User admin with our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# Customize admin site appearance
admin.site.site_header = format_html(
    '<img src="{}" width="32" height="32" style="vertical-align: middle; margin-right: 10px;"> '
    '<span style="color: #2c3e50; font-weight: 600;">Stationery Tracker</span> '
    'Admin Panel',
    static('favicon.ico')
)

admin.site.site_title = _('Stationery Tracker Administration')
admin.site.index_title = _('Stationery Tracker')

# Customize admin site colors and theme
admin.site.site_header = format_html(
    '<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); '
    'color: white; padding: 15px 20px; border-radius: 8px; '
    'margin: -15px -15px 15px 0; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">'
    '<img src="{}" width="32" height="32" style="vertical-align: middle; margin-right: 10px;"> '
    '<span style="color: white; font-weight: 600; font-size: 1.2rem;">Stationery Tracker</span> '
    '</div>',
    static('favicon.ico')
)

# Add custom CSS to admin
class CustomAdminSite(admin.AdminSite):
    site_header = admin.site.site_header
    site_title = admin.site.site_title
    
    def each_context(self, request):
        context = super().each_context(request)
        context['site_branding'] = format_html(
            '<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); '
            'color: white; padding: 10px 15px; border-radius: 6px; '
            'display: inline-block; margin: 0 10px;">'
            '<img src="{}" width="24" height="24" style="vertical-align: middle; margin-right: 8px;"> '
            '<span style="color: white; font-weight: 600;">Stationery Tracker</span></div>',
            static('favicon.ico')
        )
        return context


# Use custom admin site
admin.site = CustomAdminSite()
