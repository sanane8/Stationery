from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class Category(models.Model):
    """Category for stationery items"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class StationeryItem(models.Model):
    """Model for stationery items/commodities"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    sku = models.CharField(max_length=50, unique=True, help_text="Stock Keeping Unit")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    stock_quantity = models.PositiveIntegerField(default=0)
    minimum_stock = models.PositiveIntegerField(default=0, help_text="Minimum stock level before reorder")
    supplier = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.sku})"

    @property
    def profit_margin(self):
        """Calculate profit margin percentage"""
        if self.cost_price > 0:
            return ((self.unit_price - self.cost_price) / self.cost_price) * 100
        return 0

    @property
    def is_low_stock(self):
        """Check if item is below minimum stock level"""
        return self.stock_quantity <= self.minimum_stock


class Customer(models.Model):
    """Customer information"""
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Sale(models.Model):
    """Sales transaction model"""
    PAYMENT_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('credit', 'Credit'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    sale_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.00'))])
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cash')
    is_paid = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-sale_date']

    def __str__(self):
        return f"Sale #{self.id} - {self.customer or 'Walk-in'} - TZS {self.total_amount:,.0f}"

    @property
    def profit(self):
        """Calculate total profit for this sale.

        If the sale has line items, profit = revenue - cost of goods sold.
        If the sale has no items and appears to be a payment for a Debt, compute a
        proportional profit based on the originating sale (if any). For example,
        a partial payment for a debt created from a sale will carry the same
        fraction of the original sale's profit.
        """
        # Normal case: sale with items
        items = list(self.items.all())
        if items:
            total_cost = sum(item.item.cost_price * item.quantity for item in items)
            return self.total_amount - total_cost

        # Payment-sale case: try to infer associated debt and originating sale
        notes = (self.notes or '')
        import re
        m = re.search(r'Payment for Debt #(?P<debt_id>\d+)', notes)
        if m:
            from .models import Debt
            debt_id = int(m.group('debt_id'))
            try:
                debt = Debt.objects.get(pk=debt_id)
            except Debt.DoesNotExist:
                return self.total_amount

            # If debt points to an originating sale (the sale that created the debt), use it
            orig_sale = None
            if debt.sale and debt.sale.pk != self.pk:
                orig_sale = debt.sale

            # If we have an originating sale with calculable profit, allocate proportionally
            try:
                if orig_sale:
                    orig_profit = orig_sale.profit
                    if debt.amount and debt.amount > 0:
                        ratio = (self.total_amount / debt.amount)
                        return (orig_profit * ratio)
                # If there is no originating sale but the debt references an item/quantity
                # (i.e., manually created debt), compute the original profit as (debt.amount - total_cost)
                # where total_cost = item.cost_price * quantity, and allocate proportionally.
                if debt.item and debt.amount and debt.amount > 0:
                    total_cost = (debt.item.cost_price or Decimal('0.00')) * (debt.quantity or 1)
                    orig_profit = debt.amount - total_cost
                    ratio = (self.total_amount / debt.amount)
                    return (orig_profit * ratio)
            except Exception:
                # fall back to returning revenue if anything goes wrong
                return self.total_amount

        # Fallback for payments without originating sale: no cost information -> profit undefined
        # Treat profit as 0 to avoid overstating profit for a pure cash receipt with no COGS
        return Decimal('0')


class SaleItem(models.Model):
    """Individual items in a sale"""
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(StationeryItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    total_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])

    class Meta:
        unique_together = ['sale', 'item']

    def __str__(self):
        return f"{self.item.name} x {self.quantity} = TZS {self.total_price:,.0f}"

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        
        # Handle stock reduction
        is_new = self.pk is None
        
        if is_new:
            # New sale item - reduce stock
            if self.item.stock_quantity < self.quantity:
                raise ValueError(f"Insufficient stock. Available: {self.item.stock_quantity}, Requested: {self.quantity}")
            self.item.stock_quantity -= self.quantity
            self.item.save(update_fields=['stock_quantity'])
        else:
            # Existing sale item - adjust stock by the difference
            old_item = SaleItem.objects.get(pk=self.pk)
            old_quantity = old_item.quantity
            old_item_obj = old_item.item
            quantity_diff = self.quantity - old_quantity
            
            # If the item changed, restore stock from old item and reduce from new item
            if old_item_obj.pk != self.item.pk:
                # Restore stock to old item
                old_item_obj.stock_quantity += old_quantity
                old_item_obj.save(update_fields=['stock_quantity'])
                
                # Check and reduce stock from new item
                if self.item.stock_quantity < self.quantity:
                    raise ValueError(f"Insufficient stock. Available: {self.item.stock_quantity}, Requested: {self.quantity}")
                self.item.stock_quantity -= self.quantity
                self.item.save(update_fields=['stock_quantity'])
            else:
                # Same item - adjust by the difference
                if quantity_diff > 0:
                    # Increasing quantity - check if enough stock available
                    if self.item.stock_quantity < quantity_diff:
                        raise ValueError(f"Insufficient stock. Available: {self.item.stock_quantity}, Need additional: {quantity_diff}")
                    self.item.stock_quantity -= quantity_diff
                    self.item.save(update_fields=['stock_quantity'])
                elif quantity_diff < 0:
                    # Decreasing quantity - restore the difference
                    self.item.stock_quantity += abs(quantity_diff)
                    self.item.save(update_fields=['stock_quantity'])
                # If quantity_diff == 0, no stock adjustment needed
        
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Restore stock when sale item is deleted
        self.item.stock_quantity += self.quantity
        self.item.save(update_fields=['stock_quantity'])
        # mark as restored so post_delete signal won't double-restore
        try:
            self._stock_restored = True
        except Exception:
            pass
        super().delete(*args, **kwargs)


class Debt(models.Model):
    """Debt tracking model"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='debts')
    sale = models.ForeignKey(Sale, on_delete=models.SET_NULL, related_name='debts', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    # Link to an item and the quantity owed (required for all debts)
    # Use PROTECT to avoid accidental deletion of items referenced by debts
    item = models.ForeignKey(StationeryItem, on_delete=models.PROTECT, related_name='debts')
    quantity = models.PositiveIntegerField(default=1)

    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer.name} - TZS {self.amount:,.0f} ({self.status})"

    @property
    def remaining_amount(self):
        return self.amount - self.paid_amount

    @property
    def is_overdue(self):
        from django.utils import timezone
        return self.due_date < timezone.now().date() and self.status != 'paid'


class Payment(models.Model):
    """Payment records for debts"""
    debt = models.ForeignKey(Debt, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=20, choices=Sale.PAYMENT_CHOICES, default='cash')
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-payment_date']

    def __str__(self):
        return f"Payment of TZS {self.amount:,.0f} for {self.debt.customer.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update debt status
        self.debt.paid_amount += self.amount
        if self.debt.paid_amount >= self.debt.amount:
            self.debt.status = 'paid'
        elif self.debt.paid_amount > 0:
            self.debt.status = 'partial'
        self.debt.save()


class Expenditure(models.Model):
    """Track business expenditures (money going out)."""
    CATEGORY_CHOICES = [
        ('supplies', 'Supplies'),
        ('rent', 'Rent'),
        ('utilities', 'Utilities'),
        ('salary', 'Salary'),
        ('marketing', 'Marketing'),
        ('other', 'Other'),
    ]

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    expense_date = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-expense_date']

    def __str__(self):
        return f"{self.get_category_display()} - TZS {self.amount:,.0f} on {self.expense_date.date()}"
