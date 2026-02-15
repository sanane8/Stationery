from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from django.utils import timezone
from .models import Category, StationeryItem, Customer, Sale, SaleItem, Debt, Payment
from .models import Expenditure, UserProfile


class RestrictedModelAdmin(admin.ModelAdmin):
    """Custom ModelAdmin that bypasses Django permissions for our role system"""
    
    def has_view_permission(self, request, obj=None):
        """Allow admin users to view"""
        try:
            return request.user.profile.is_admin()
        except:
            return False
    
    def has_change_permission(self, request, obj=None):
        """Allow admin users to change"""
        try:
            return request.user.profile.is_admin()
        except:
            return False
    
    def has_add_permission(self, request):
        """Allow admin users to add"""
        try:
            return request.user.profile.is_admin()
        except:
            return False
    
    def has_delete_permission(self, request, obj=None):
        """Allow admin users to delete"""
        try:
            return request.user.profile.is_admin()
        except:
            return False
    
    def has_module_permission(self, request):
        """Allow admin users to see module"""
        try:
            return request.user.profile.is_admin()
        except:
            return False


# Regular admin classes for registration
class CategoryAdmin(RestrictedModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at']


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1


class StationeryItemAdmin(RestrictedModelAdmin):
    list_display = ['name', 'sku', 'category', 'unit_price', 'cost_price', 'stock_quantity', 'profit_margin_display', 'is_low_stock_display', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'sku', 'supplier']
    list_editable = ['unit_price', 'cost_price', 'stock_quantity', 'is_active']
    readonly_fields = ['profit_margin_display', 'is_low_stock_display']
    ordering = ['name']

    def profit_margin_display(self, obj):
        if obj and hasattr(obj, 'profit_margin'):
            return f"{obj.profit_margin:.1f}%"
        return "0.0%"
    profit_margin_display.short_description = "Profit Margin"

    def is_low_stock_display(self, obj):
        if obj and hasattr(obj, 'is_low_stock'):
            if obj.is_low_stock:
                return format_html('<span style="color: red;">LOW STOCK</span>')
            return format_html('<span style="color: green;">OK</span>')
        return format_html('<span style="color: gray;">N/A</span>')
    is_low_stock_display.short_description = "Stock Status"


class CustomerAdmin(RestrictedModelAdmin):
    list_display = ['name', 'email', 'phone', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'email', 'phone']
    list_editable = ['is_active']


class SaleAdmin(RestrictedModelAdmin):
    list_display = ['id', 'customer', 'sale_date_local', 'total_amount', 'payment_method', 'is_paid', 'profit_display', 'created_by']
    list_filter = ['payment_method', 'is_paid', 'sale_date', 'created_by']
    search_fields = ['customer__name', 'notes']
    readonly_fields = ['profit_display']
    inlines = [SaleItemInline]
    actions = ['delete_and_restore_stock']

    def profit_display(self, obj):
        return f"${obj.profit:.2f}"
    profit_display.short_description = "Profit"

    def sale_date_local(self, obj):
        if not obj.sale_date:
            return '-'
        local_dt = timezone.localtime(obj.sale_date)
        return local_dt.strftime('%b %d, %Y %H:%M')
    sale_date_local.admin_order_field = 'sale_date'
    sale_date_local.short_description = 'Sale Date'

    def delete_and_restore_stock(self, request, queryset):
        """Admin action to delete selected sales and show restored stock in a message."""
        # Collect restored quantities per item name
        restored = {}
        total_sales = queryset.count()
        for sale in queryset:
            for si in sale.items.all():
                name = si.item.name
                restored[name] = restored.get(name, 0) + si.quantity

        # Perform deletion (this will trigger signals to restore stock for bulk deletes)
        queryset.delete()

        if restored:
            parts = [f"{name} (+{qty})" for name, qty in restored.items()]
            messages.success(request, f"Deleted {total_sales} sale(s). Restored stock: {', '.join(parts)}")
        else:
            messages.success(request, f"Deleted {total_sales} sale(s).")

    delete_and_restore_stock.short_description = "Delete selected sales and restore stock (show restored items)"


class SaleItemAdmin(RestrictedModelAdmin):
    list_display = ['sale', 'item', 'quantity', 'unit_price', 'total_price']
    list_filter = ['sale__sale_date']


class DebtAdmin(RestrictedModelAdmin):
    list_display = ['customer', 'amount', 'paid_amount', 'remaining_amount', 'due_date', 'status', 'is_overdue_display']
    list_filter = ['status', 'due_date', 'created_at']
    search_fields = ['customer__name', 'description']
    readonly_fields = ['remaining_amount', 'is_overdue_display']

    def is_overdue_display(self, obj):
        if obj.is_overdue:
            return format_html('<span style="color: red;">OVERDUE</span>')
        return format_html('<span style="color: green;">OK</span>')
    is_overdue_display.short_description = "Overdue Status"


class PaymentAdmin(RestrictedModelAdmin):
    list_display = ['debt', 'amount', 'payment_date', 'payment_method']
    list_filter = ['payment_method', 'payment_date']
    search_fields = ['debt__customer__name', 'notes']


class ExpenditureAdmin(RestrictedModelAdmin):
    list_display = ['id', 'category', 'amount', 'expense_date', 'created_by']
    list_filter = ['category', 'expense_date']
    search_fields = ['description']
    readonly_fields = ['created_at']


class UserProfileAdmin(RestrictedModelAdmin):
    list_display = ['user', 'role', 'phone', 'created_at', 'updated_at']
    list_filter = ['role', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone']
    list_editable = ['role', 'phone']


# Function to register models with restricted admin site
def register_with_restricted_admin(admin_site):
    """Register all models with the restricted admin site"""
    admin_site.register(Category, CategoryAdmin)
    admin_site.register(StationeryItem, StationeryItemAdmin)
    admin_site.register(Customer, CustomerAdmin)
    admin_site.register(Sale, SaleAdmin)
    admin_site.register(SaleItem, SaleItemAdmin)
    admin_site.register(Debt, DebtAdmin)
    admin_site.register(Payment, PaymentAdmin)
    admin_site.register(Expenditure, ExpenditureAdmin)
    admin_site.register(UserProfile, UserProfileAdmin)
