from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import datetime, timedelta
from .models import StationeryItem, Sale, Debt, Customer, Category
from .forms import SaleForm, SaleItemForm, DebtForm, PaymentForm, StationeryItemForm, CustomerForm


def dashboard(request):
    """Main dashboard view"""
    # Get recent sales
    recent_sales = Sale.objects.select_related('customer').order_by('-sale_date')[:10]
    
    # Get low stock items
    low_stock_items = StationeryItem.objects.filter(
        stock_quantity__lte=models.F('minimum_stock'),
        is_active=True
    )
    
    # Get overdue debts
    overdue_debts = Debt.objects.filter(
        due_date__lt=timezone.now().date(),
        status__in=['pending', 'partial']
    ).select_related('customer')
    
    # Calculate totals for today
    today = timezone.now().date()
    today_sales = Sale.objects.filter(sale_date__date=today).aggregate(
        total_sales=Sum('total_amount'),
        count_sales=Count('id')
    )
    
    # Calculate monthly totals
    month_start = today.replace(day=1)
    monthly_sales = Sale.objects.filter(sale_date__date__gte=month_start).aggregate(
        total_sales=Sum('total_amount'),
        count_sales=Count('id')
    )
    
    # Get total outstanding debt
    total_debt = Debt.objects.filter(status__in=['pending', 'partial']).aggregate(
        total=Sum('amount') - Sum('paid_amount')
    )['total'] or 0
    
    context = {
        'recent_sales': recent_sales,
        'low_stock_items': low_stock_items,
        'overdue_debts': overdue_debts,
        'today_sales': today_sales,
        'monthly_sales': monthly_sales,
        'total_debt': total_debt,
    }
    
    return render(request, 'tracker/dashboard.html', context)


def stationery_list(request):
    """List all stationery items"""
    items = StationeryItem.objects.select_related('category').filter(is_active=True)
    
    # Filter by category if specified
    category_id = request.GET.get('category')
    if category_id:
        items = items.filter(category_id=category_id)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        items = items.filter(
            Q(name__icontains=search_query) | 
            Q(sku__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    categories = Category.objects.all()
    
    context = {
        'items': items,
        'categories': categories,
        'selected_category': category_id,
        'search_query': search_query,
    }
    
    return render(request, 'tracker/stationery_list.html', context)


def stationery_detail(request, pk):
    """Detail view for a stationery item"""
    item = get_object_or_404(StationeryItem, pk=pk)
    recent_sales = Sale.objects.filter(items__item=item).order_by('-sale_date')[:10]
    
    context = {
        'item': item,
        'recent_sales': recent_sales,
    }
    
    return render(request, 'tracker/stationery_detail.html', context)


def sales_list(request):
    """List all sales"""
    sales = Sale.objects.select_related('customer', 'created_by').order_by('-sale_date')
    
    # Filter by date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        sales = sales.filter(sale_date__date__gte=start_date)
    if end_date:
        sales = sales.filter(sale_date__date__lte=end_date)
    
    # Filter by payment status
    payment_status = request.GET.get('payment_status')
    if payment_status == 'paid':
        sales = sales.filter(is_paid=True)
    elif payment_status == 'unpaid':
        sales = sales.filter(is_paid=False)
    
    context = {
        'sales': sales,
        'start_date': start_date,
        'end_date': end_date,
        'payment_status': payment_status,
    }
    
    return render(request, 'tracker/sales_list.html', context)


def sale_detail(request, pk):
    """Detail view for a sale"""
    sale = get_object_or_404(Sale, pk=pk)
    sale_items = sale.items.select_related('item')
    
    context = {
        'sale': sale,
        'sale_items': sale_items,
    }
    
    return render(request, 'tracker/sale_detail.html', context)


@login_required
def create_sale(request):
    """Create a new sale"""
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            sale = form.save(commit=False)
            sale.created_by = request.user
            # Set a default total_amount for now (will be calculated when items are added)
            sale.total_amount = 0.00
            sale.save()
            messages.success(request, 'Sale created successfully! You can now add items to this sale.')
            return redirect('sale_detail', pk=sale.pk)
    else:
        form = SaleForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'tracker/sale_form.html', context)


@login_required
def add_sale_item(request, sale_id):
    """Add an item to a sale"""
    sale = get_object_or_404(Sale, pk=sale_id)
    
    if request.method == 'POST':
        form = SaleItemForm(request.POST)
        if form.is_valid():
            sale_item = form.save(commit=False)
            sale_item.sale = sale
            sale_item.save()
            
            # Update sale total amount
            sale.total_amount = sum(item.total_price for item in sale.items.all())
            sale.save()
            
            messages.success(request, 'Item added to sale successfully!')
            return redirect('sale_detail', pk=sale.pk)
    else:
        form = SaleItemForm()
    
    context = {
        'form': form,
        'sale': sale,
    }
    
    return render(request, 'tracker/add_sale_item.html', context)


def debts_list(request):
    """List all debts"""
    debts = Debt.objects.select_related('customer').order_by('-created_at')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        debts = debts.filter(status=status)
    
    # Filter by overdue
    overdue_only = request.GET.get('overdue')
    if overdue_only:
        debts = debts.filter(due_date__lt=timezone.now().date(), status__in=['pending', 'partial'])
    
    context = {
        'debts': debts,
        'selected_status': status,
        'overdue_only': overdue_only,
    }
    
    return render(request, 'tracker/debts_list.html', context)


def debt_detail(request, pk):
    """Detail view for a debt"""
    debt = get_object_or_404(Debt, pk=pk)
    payments = debt.payments.all().order_by('-payment_date')
    
    context = {
        'debt': debt,
        'payments': payments,
    }
    
    return render(request, 'tracker/debt_detail.html', context)


@login_required
def create_debt(request):
    """Create a new debt"""
    if request.method == 'POST':
        form = DebtForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Debt created successfully!')
            return redirect('debts_list')
    else:
        form = DebtForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'tracker/debt_form.html', context)


@login_required
def add_payment(request, debt_id):
    """Add a payment to a debt"""
    debt = get_object_or_404(Debt, pk=debt_id)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.debt = debt
            payment.save()
            messages.success(request, 'Payment added successfully!')
            return redirect('debt_detail', pk=debt.pk)
    else:
        form = PaymentForm()
    
    context = {
        'form': form,
        'debt': debt,
    }
    
    return render(request, 'tracker/payment_form.html', context)


def customers_list(request):
    """List all customers"""
    customers = Customer.objects.filter(is_active=True).order_by('name')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        customers = customers.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    context = {
        'customers': customers,
        'search_query': search_query,
    }
    
    return render(request, 'tracker/customers_list.html', context)


def customer_detail(request, pk):
    """Detail view for a customer"""
    customer = get_object_or_404(Customer, pk=pk)
    sales = customer.sale_set.all().order_by('-sale_date')[:10]
    debts = customer.debts.all().order_by('-created_at')
    
    context = {
        'customer': customer,
        'sales': sales,
        'debts': debts,
    }
    
    return render(request, 'tracker/customer_detail.html', context)


@login_required
def create_customer(request):
    """Create a new customer"""
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer created successfully!')
            return redirect('customers_list')
    else:
        form = CustomerForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'tracker/customer_form.html', context)


@login_required
def create_stationery_item(request):
    """Create a new stationery item"""
    if request.method == 'POST':
        form = StationeryItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Stationery item created successfully!')
            return redirect('stationery_list')
    else:
        form = StationeryItemForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'tracker/stationery_form.html', context)
