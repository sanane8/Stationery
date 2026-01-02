from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from django.db import transaction
from django.db.models import Sum, Count, Q, F, DecimalField, ExpressionWrapper
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from .models import StationeryItem, Sale, SaleItem, Debt, Customer, Category
from .forms import SaleForm, SaleItemForm, DebtForm, PaymentForm, StationeryItemForm, CustomerForm
from .forms import ExpenditureForm
from .models import Expenditure
import csv
from django.http import HttpResponse
from io import BytesIO
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False


def dashboard(request):
    """Main dashboard view"""
    # Get recent **paid** sales (exclude unpaid sales from 'recent' listing)
    recent_sales = Sale.objects.select_related('customer').filter(is_paid=True).order_by('-sale_date')[:10]

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
    
    # Calculate totals for today using timezone-aware range to avoid date-boundary issues
    now_local = timezone.localtime(timezone.now())
    today_start = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    # Exclude unpaid sales from today's totals
    today_sales = Sale.objects.filter(sale_date__gte=today_start, sale_date__lt=today_end, is_paid=True).aggregate(
        total_sales=Sum('total_amount'),
        count_sales=Count('id')
    )

    # Today's expenditures (used to compute net sales)
    exp_today = Expenditure.objects.filter(expense_date__gte=today_start, expense_date__lt=today_end).aggregate(
        total=Sum('amount'), count=Count('id')
    )

    # Compute net today's sales (sales minus today's expenditures)
    today_total = today_sales.get('total_sales') or 0
    today_exp = exp_today.get('total') or 0
    net_today_sales = today_total - today_exp

    # Calculate monthly totals using local timezone month range (exclude unpaid sales)
    month_start = today_start.replace(day=1)
    # find start of next month
    next_month = (month_start + timedelta(days=32)).replace(day=1)
    monthly_sales = Sale.objects.filter(sale_date__gte=month_start, sale_date__lt=next_month, is_paid=True).aggregate(
        total_sales=Sum('total_amount'),
        count_sales=Count('id')
    )

    exp_month = Expenditure.objects.filter(expense_date__gte=month_start, expense_date__lt=next_month).aggregate(
        total=Sum('amount'), count=Count('id')
    )
    month_total = monthly_sales.get('total_sales') or 0
    month_exp = exp_month.get('total') or 0
    net_monthly_sales = month_total - month_exp
    
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
        'exp_today': exp_today,
        'exp_month': exp_month,
        'net_today_sales': net_today_sales,
        'net_monthly_sales': net_monthly_sales,
    }
    
    return render(request, 'tracker/dashboard.html', context)


def stationery_list(request):
    """List all stationery items"""
    # Include active items and any legacy items where is_active might be null
    # Start from all items; we'll restrict to active-only unless 'inactive' toggle is set
    items = StationeryItem.objects.select_related('category').all()

    # Filter by category if specified
    category_id = request.GET.get('category')
    if category_id:
        items = items.filter(category_id=category_id)

    # Search functionality (apply before computing counts so counts reflect the current scope)
    raw_search = request.GET.get('search')
    if raw_search and raw_search.strip().lower() != 'none':
        search_query = raw_search.strip()
        items = items.filter(
            Q(name__icontains=search_query) | 
            Q(sku__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    else:
        search_query = ''

    # Low-stock and inactive filters
    low_stock_flag = request.GET.get('low_stock')
    inactive_flag = request.GET.get('inactive')

    selected_low_stock = False
    selected_inactive = False

    # By default, show only active items; if inactive checkbox is set, we'll defer filtering until after counts
    if inactive_flag in (None, '', 'None'):
        items = items.filter(Q(is_active=True) | Q(is_active__isnull=True))
    else:
        selected_inactive = True

    # Compute counts in the current search/category scope (respecting the default active/inactive selection)
    low_stock_count = items.filter(stock_quantity__lte=models.F('minimum_stock')).count()
    inactive_count = items.filter(is_active=False).count()

    if low_stock_flag not in (None, '', 'None'):
        selected_low_stock = True
        items = items.filter(stock_quantity__lte=models.F('minimum_stock'))

    # If inactive checkbox is explicitly selected, show only inactive items
    if selected_inactive:
        items = items.filter(is_active=False)
    
    categories = Category.objects.all()
    
    # Paginate
    page = request.GET.get('page')
    paginator = Paginator(items, 20)
    page_obj = paginator.get_page(page)

    context = {
        'items': page_obj,
        'categories': categories,
        'selected_category': category_id,
        'search_query': search_query,
        'paginator': paginator,
        'page_obj': page_obj,
        'selected_low_stock': selected_low_stock,
        'low_stock_count': low_stock_count,
        'selected_inactive': selected_inactive,
        'inactive_count': inactive_count,
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
    # guard against literal 'None' or empty strings passed from templates
    if start_date in (None, '', 'None'):
        start_date = None
    if end_date in (None, '', 'None'):
        end_date = None
    
    if start_date:
        sales = sales.filter(sale_date__date__gte=start_date)
    if end_date:
        sales = sales.filter(sale_date__date__lte=end_date)
    
    # Filter by payment status
    raw_payment_status = request.GET.get('payment_status')
    if raw_payment_status in (None, '', 'None'):
        # No explicit filter provided by user; default to showing paid sales
        payment_status = 'paid'
        payment_status_explicit = False
    else:
        payment_status = raw_payment_status
        payment_status_explicit = True

    if payment_status == 'paid':
        sales = sales.filter(is_paid=True)
    elif payment_status == 'unpaid':
        sales = sales.filter(is_paid=False)
    elif payment_status == 'all':
        # explicit request to include all sales
        pass

    # Annotate per-sale total_cost and profit to avoid N+1 queries in template
    total_cost_expr = Sum(F('items__quantity') * F('items__item__cost_price'), output_field=DecimalField())
    sales = sales.annotate(total_cost=total_cost_expr)
    # Use a different name for the annotated profit so we don't shadow the model's `profit` property
    sales = sales.annotate(annotated_profit=ExpressionWrapper(F('total_amount') - F('total_cost'), output_field=DecimalField()))
    
    # Calculate total amount and overall profit for filtered sales
    agg = sales.aggregate(total_revenue=Sum('total_amount'), total_cost=Sum(F('items__quantity') * F('items__item__cost_price'), output_field=DecimalField()))
    total_amount = agg.get('total_revenue') or Decimal('0')
    overall_cost = agg.get('total_cost') or Decimal('0')
    overall_profit = total_amount - overall_cost

    # Compute total expenditures for the same filter window (if date filters applied)
    exp_qs = Expenditure.objects.all()
    if start_date:
        exp_qs = exp_qs.filter(expense_date__date__gte=start_date)
    if end_date:
        exp_qs = exp_qs.filter(expense_date__date__lte=end_date)
    total_expenditure = exp_qs.aggregate(total=Sum('amount'))['total'] or Decimal('0')

    # Net total amount after subtracting expenditures
    total_amount_net = total_amount - total_expenditure

    # Calculate daily aggregates (local timezone-aware) for the filtered sales.
    # We group sales by their *local* date (timezone.localtime(sale.sale_date).date()) so
    # daily buckets match what's shown in the dashboard and templates.
    daily_map = {}
    # Use a separate queryset for aggregation to avoid confusing pagination (evaluate full set)
    sales_for_agg = sales.select_related('customer').prefetch_related('items__item')

    for sale in sales_for_agg:
        local_date = timezone.localtime(sale.sale_date).date()
        rev = sale.total_amount or Decimal('0')
        try:
            cost = sum((si.quantity * (si.item.cost_price or Decimal('0'))) for si in sale.items.all())
        except Exception:
            cost = Decimal('0')

        entry = daily_map.setdefault(local_date, {'revenue': Decimal('0'), 'cost': Decimal('0'), 'count': 0})
        entry['revenue'] += rev
        entry['cost'] += cost
        entry['count'] += 1

    # Convert map into sorted list (newest date first)
    daily_sales = []
    for date_key in sorted(daily_map.keys(), reverse=True):
        data = daily_map[date_key]
        # Subtract expenditures for this date
        exp_for_date = Expenditure.objects.filter(expense_date__date=date_key).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        net_revenue = data['revenue'] - (exp_for_date or Decimal('0'))
        profit = net_revenue - data['cost']
        daily_sales.append({
            'date': date_key,
            'revenue': net_revenue,
            'cost': data['cost'],
            'expenditure': exp_for_date,
            'profit': profit,
            'count': data['count'],
        })

    # By default (when no filters applied) show only the most recent two days
    # Use `payment_status_explicit` to detect whether user provided a filter;
    # if not provided, we treat the page as having no user filters and shorten the summary.
    if not (start_date or end_date or (locals().get('payment_status_explicit', False))):
        daily_sales = daily_sales[:2]
    
    # Paginate
    page = request.GET.get('page')
    paginator = Paginator(sales, 20)
    page_obj = paginator.get_page(page)

    # Ensure payment-sales (which have no SaleItem rows) display a sensible profit
    # annotated_profit may be NULL for such rows; compute from model property in Python
    for sale in page_obj.object_list:
        if getattr(sale, 'annotated_profit', None) is None:
            try:
                sale.annotated_profit = sale.profit
            except Exception:
                sale.annotated_profit = Decimal('0')

    context = {
        'sales': page_obj,
        'start_date': start_date,
        'end_date': end_date,
        'payment_status': payment_status,
        'total_amount': total_amount,
        'total_amount_net': total_amount_net,
        'total_expenditure': total_expenditure,
        'daily_sales': daily_sales,
        'overall_profit': overall_profit,
        'paginator': paginator,
        'page_obj': page_obj,
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


def sales_daily_export_csv(request):
    """Export daily sales summary (respecting same filters) as CSV."""
    sales = Sale.objects.select_related('customer', 'created_by').order_by('-sale_date')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    payment_status = request.GET.get('payment_status')
    # guard against literal 'None' or empty strings
    if start_date in (None, '', 'None'):
        start_date = None
    if end_date in (None, '', 'None'):
        end_date = None
    if payment_status in (None, '', 'None'):
        payment_status = None

    if start_date:
        sales = sales.filter(sale_date__date__gte=start_date)
    if end_date:
        sales = sales.filter(sale_date__date__lte=end_date)
    if payment_status == 'paid':
        sales = sales.filter(is_paid=True)
    elif payment_status == 'unpaid':
        sales = sales.filter(is_paid=False)
    # Export all matching sales (row per sale) as CSV
    sales = sales.select_related('customer').prefetch_related('items__item')

    try:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="all_sales.csv"'
        writer = csv.writer(response)
        # Header
        writer.writerow(['Sale ID', 'Date', 'Customer', 'Amount', 'Profit', 'Payment Method', 'Status', 'Created By'])

        for sale in sales:
            # compute total cost for the sale
            try:
                total_cost = sum((si.quantity * (si.item.cost_price or Decimal('0'))) for si in sale.items.all())
            except Exception:
                total_cost = Decimal('0')
            revenue = sale.total_amount or Decimal('0')
            # If sale has items, profit is revenue - total_cost; otherwise, try to use Sale.profit
            if sale.items.exists():
                profit = revenue - (total_cost or Decimal('0'))
            else:
                try:
                    profit = sale.profit
                except Exception:
                    profit = Decimal('0')

            # format
            try:
                date_str = timezone.localtime(sale.sale_date).strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                date_str = str(sale.sale_date)

            created_by = sale.created_by.get_full_name() if sale.created_by else ''
            customer = sale.customer.name if sale.customer else 'Walk-in'

            amount_str = format(revenue, ',.0f')
            profit_str = format(profit, ',.0f')

            writer.writerow([
                sale.id,
                date_str,
                customer,
                amount_str,
                profit_str,
                sale.get_payment_method_display(),
                'Paid' if sale.is_paid else 'Unpaid',
                created_by,
            ])

        return response
    except Exception:
        messages.error(request, 'Failed to export sales CSV. Please try again.')
        return redirect('sales_list')


def sales_daily_export_pdf(request):
    """Export daily sales summary as PDF using ReportLab."""
    if not REPORTLAB_AVAILABLE:
        messages.error(request, 'PDF export requires the ReportLab package. Install it with `pip install reportlab`.')
        return redirect('sales_list')

    sales = Sale.objects.select_related('customer', 'created_by').order_by('-sale_date')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    payment_status = request.GET.get('payment_status')
    # guard against literal 'None' or empty strings
    if start_date in (None, '', 'None'):
        start_date = None
    if end_date in (None, '', 'None'):
        end_date = None
    if payment_status in (None, '', 'None'):
        payment_status = None

    if start_date:
        sales = sales.filter(sale_date__date__gte=start_date)
    if end_date:
        sales = sales.filter(sale_date__date__lte=end_date)
    if payment_status == 'paid':
        sales = sales.filter(is_paid=True)
    elif payment_status == 'unpaid':
        sales = sales.filter(is_paid=False)

    # Export all matching sales (no two-day cap) as a PDF listing individual sales
    # Build list of sales respecting filters
    sales = sales.select_related('customer').prefetch_related('items__item')

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margin = 15 * mm
    y = height - margin

    p.setFont('Helvetica-Bold', 14)
    p.drawString(margin, y, 'All Sales Report')
    y -= 10 * mm
    p.setFont('Helvetica-Bold', 10)
    # Header row
    p.drawString(margin, y, 'Sale #')
    p.drawString(margin + 25 * mm, y, 'Date')
    p.drawString(margin + 65 * mm, y, 'Customer')
    p.drawString(margin + 120 * mm, y, 'Amount')
    p.drawString(margin + 150 * mm, y, 'Profit')
    y -= 6 * mm
    p.setFont('Helvetica', 10)

    for sale in sales:
        # Paginate
        if y < margin + 20 * mm:
            p.showPage()
            y = height - margin
            p.setFont('Helvetica', 10)

        # Compute cost for the sale by summing related items
        try:
            total_cost = sum((si.quantity * (si.item.cost_price or Decimal('0'))) for si in sale.items.all())
        except Exception:
            total_cost = Decimal('0')
        revenue = sale.total_amount or Decimal('0')
        profit = revenue - (total_cost or Decimal('0'))

        date_str = ''
        try:
            date_str = timezone.localtime(sale.sale_date).strftime('%Y-%m-%d')
        except Exception:
            date_str = str(sale.sale_date)

        customer_name = sale.customer.name if sale.customer else 'Walk-in'

        amount_str = format(revenue, ',.0f')
        profit_str = format(profit, ',.0f')

        p.drawString(margin, y, f"#{sale.id}")
        p.drawString(margin + 25 * mm, y, date_str)
        p.drawString(margin + 65 * mm, y, customer_name[:22])
        p.drawRightString(margin + 145 * mm, y, amount_str)
        p.drawRightString(margin + 175 * mm, y, profit_str)

        y -= 6 * mm

    p.showPage()
    p.save()
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="all_sales.pdf"'
    return response


def sales_daily_print(request):
    """Render a print-friendly HTML view of the daily sales summary."""
    # Render a print-friendly HTML listing of all matching sales (one row per sale)
    sales = Sale.objects.select_related('customer', 'created_by').order_by('-sale_date')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    payment_status = request.GET.get('payment_status')
    # guard against literal 'None' or empty strings
    if start_date in (None, '', 'None'):
        start_date = None
    if end_date in (None, '', 'None'):
        end_date = None
    if payment_status in (None, '', 'None'):
        payment_status = None

    if start_date:
        sales = sales.filter(sale_date__date__gte=start_date)
    if end_date:
        sales = sales.filter(sale_date__date__lte=end_date)
    if payment_status == 'paid':
        sales = sales.filter(is_paid=True)
    elif payment_status == 'unpaid':
        sales = sales.filter(is_paid=False)

    sales = sales.select_related('customer').prefetch_related('items__item')

    rows = []
    for sale in sales:
        try:
            total_cost = sum((si.quantity * (si.item.cost_price or Decimal('0'))) for si in sale.items.all())
        except Exception:
            total_cost = Decimal('0')
        revenue = sale.total_amount or Decimal('0')
        profit = revenue - (total_cost or Decimal('0'))

        try:
            date_str = timezone.localtime(sale.sale_date).strftime('%Y-%m-%d %H:%M')
        except Exception:
            date_str = str(sale.sale_date)

        rows.append({
            'id': sale.id,
            'date': date_str,
            'customer': sale.customer.name if sale.customer else 'Walk-in',
            'amount': revenue,
            'profit': profit,
            'payment_method': sale.get_payment_method_display(),
            'status': 'Paid' if sale.is_paid else 'Unpaid',
            'created_by': sale.created_by.get_full_name() if sale.created_by else '',
        })

    context = {
        'sales_rows': rows,
        'start_date': start_date,
        'end_date': end_date,
        'payment_status': payment_status,
    }

    return render(request, 'tracker/sales_all_print.html', context)


@login_required
def delete_sale(request, pk):
    """Delete a sale and inform the user about restored stock."""
    sale = get_object_or_404(Sale, pk=pk)

    if request.method == 'POST':
        # Capture restored items info before deletion
        restored_items = []
        for si in sale.items.all():
            restored_items.append(f"{si.item.name} (+{si.quantity})")

        sale.delete()

        if restored_items:
            messages.success(request, f"Sale deleted. Restored stock: {', '.join(restored_items)}")
        else:
            messages.success(request, "Sale deleted.")

        return redirect('sales_list')

    # GET -> show confirmation
    return render(request, 'tracker/confirm_delete_sale.html', {'sale': sale})


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
    # We will lock the Sale row during item addition to avoid race conditions
    if request.method == 'POST':
        form = SaleItemForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Lock the sale row for this transaction so concurrent requests serialize
                    sale = Sale.objects.select_for_update().get(pk=sale_id)

                    sale_item = form.save(commit=False)
                    sale_item.sale = sale

                    # Check if this sale already has the same item
                    existing_item = None
                    try:
                        existing_item = SaleItem.objects.get(sale=sale, item=sale_item.item)
                    except SaleItem.DoesNotExist:
                        existing_item = None

                    # If it's a new line item, ensure stock exists for the requested quantity
                    if existing_item is None and sale_item.item.stock_quantity < sale_item.quantity:
                        messages.error(request, f'Insufficient stock! Available: {sale_item.item.stock_quantity}, Requested: {sale_item.quantity}')
                        context = {
                            'form': form,
                            'sale': sale,
                        }
                        return render(request, 'tracker/add_sale_item.html', context)

                    try:
                        # If the item already exists on the sale, increase its quantity instead of creating a duplicate
                        merged = False
                        additional = 0
                        if existing_item:
                            additional = sale_item.quantity
                            if sale_item.item.stock_quantity < additional:
                                messages.error(request, f'Insufficient stock! Available: {sale_item.item.stock_quantity}, Requested additional: {additional}')
                                context = {
                                    'form': form,
                                    'sale': sale,
                                }
                                return render(request, 'tracker/add_sale_item.html', context)

                            existing_item.quantity = existing_item.quantity + additional
                            # Update unit_price to the latest provided price (could choose to keep existing)
                            existing_item.unit_price = sale_item.unit_price
                            existing_item.save()
                            merged = True
                        else:
                            sale_item.save()

                        # Recompute sale total from DB to ensure accuracy under concurrency
                        aggregated = SaleItem.objects.filter(sale=sale).aggregate(total=Sum('total_price'))
                        total = aggregated['total'] or Decimal('0')
                        sale.total_amount = total
                        sale.save(update_fields=['total_amount'])

                        if merged:
                            messages.success(request, f'Item quantity updated; merged additional {additional} units into the existing line.')
                        else:
                            messages.success(request, 'Item added to sale successfully! Stock has been updated.')

                        return redirect('sale_detail', pk=sale.pk)
                    except ValueError as e:
                        # Handle stock validation error from model (for updates or race conditions)
                        messages.error(request, str(e))
                        context = {
                            'form': form,
                            'sale': sale,
                        }
                        return render(request, 'tracker/add_sale_item.html', context)
            except Sale.DoesNotExist:
                messages.error(request, 'Sale not found.')
                return redirect('sales_list')
    else:
        # For GET, just fetch the sale for context
        sale = get_object_or_404(Sale, pk=sale_id)
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
        if status == 'overdue':
            debts = debts.filter(
                due_date__lt=timezone.now().date(),
                status__in=['pending', 'partial']
            )
        else:
            debts = debts.filter(status=status)
    
    # Filter by customer
    customer_id = request.GET.get('customer')
    if customer_id:
        debts = debts.filter(customer_id=customer_id)
    
    # Filter by overdue
    overdue_only = request.GET.get('overdue')
    if overdue_only:
        debts = debts.filter(due_date__lt=timezone.now().date(), status__in=['pending', 'partial'])

    # Search functionality (searches description when customer is selected, or customer name + description when not)
    search_query = request.GET.get('search')
    if search_query:
        if customer_id:
            # When customer is selected, only search in description
            debts = debts.filter(description__icontains=search_query)
        else:
            # When no customer selected, search in customer name and description
            debts = debts.filter(
                Q(customer__name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
    
    # Get all customers for the dropdown
    customers = Customer.objects.filter(is_active=True).order_by('name')
    
    # Totals for the filtered dataset
    totals = debts.aggregate(
        total_amount=Sum('amount'),
        total_paid=Sum('paid_amount')
    )
    total_amount = totals['total_amount'] or Decimal('0')
    total_paid = totals['total_paid'] or Decimal('0')
    total_remaining = total_amount - total_paid
    
    # Paginate
    page = request.GET.get('page')
    paginator = Paginator(debts, 20)
    page_obj = paginator.get_page(page)

    context = {
        'debts': page_obj,
        'customers': customers,
        'selected_status': status,
        'selected_customer': customer_id,
        'overdue_only': overdue_only,
        'search_query': search_query,
        'total_paid': total_paid,
        'total_remaining': total_remaining,
        'paginator': paginator,
        'page_obj': page_obj,
    }

    return render(request, 'tracker/debts_list.html', context)


def expenditures_list(request):
    """List expenditures and totals"""
    expenditures = Expenditure.objects.all().order_by('-expense_date')

    # Filter by date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    # guard against literal 'None' or empty strings from template/query
    if start_date in (None, '', 'None'):
        start_date = None
    if end_date in (None, '', 'None'):
        end_date = None
    if start_date:
        expenditures = expenditures.filter(expense_date__date__gte=start_date)
    if end_date:
        expenditures = expenditures.filter(expense_date__date__lte=end_date)

    total_spent = expenditures.aggregate(total=Sum('amount'))['total'] or Decimal('0')

    # Paginate
    page = request.GET.get('page')
    paginator = Paginator(expenditures, 20)
    page_obj = paginator.get_page(page)

    context = {
        'expenditures': page_obj,
        'start_date': start_date,
        'end_date': end_date,
        'total_spent': total_spent,
        'paginator': paginator,
        'page_obj': page_obj,
    }
    return render(request, 'tracker/expenditures_list.html', context)


@login_required
def create_expenditure(request):
    if request.method == 'POST':
        form = ExpenditureForm(request.POST)
        if form.is_valid():
            exp = form.save(commit=False)
            exp.created_by = request.user
            exp.save()
            messages.success(request, 'Expenditure recorded successfully.')
            return redirect('expenditures_list')
    else:
        form = ExpenditureForm()

    return render(request, 'tracker/expenditure_form.html', {'form': form})


@login_required
def delete_expenditure(request, pk):
    """Delete an expenditure entry after confirmation."""
    exp = get_object_or_404(Expenditure, pk=pk)

    if request.method == 'POST':
        exp.delete()
        messages.success(request, 'Expenditure deleted successfully.')
        return redirect('expenditures_list')

    return render(request, 'tracker/confirm_delete_expenditure.html', {'expenditure': exp})


def expenditures_export_csv(request):
    """Export filtered expenditures as CSV"""
    expenditures = Expenditure.objects.all().order_by('-expense_date')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date in (None, '', 'None'):
        start_date = None
    if end_date in (None, '', 'None'):
        end_date = None
    if start_date:
        expenditures = expenditures.filter(expense_date__date__gte=start_date)
    if end_date:
        expenditures = expenditures.filter(expense_date__date__lte=end_date)

    try:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="expenditures.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Category', 'Description', 'Date', 'Amount', 'Created By'])
        for e in expenditures:
            # ensure we can format fields safely
            date_str = ''
            try:
                date_str = timezone.localtime(e.expense_date).strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                date_str = str(e.expense_date)

            created_by = ''
            try:
                created_by = e.created_by.username if e.created_by else ''
            except Exception:
                created_by = ''

            writer.writerow([
                e.id,
                e.get_category_display(),
                e.description or '',
                date_str,
                f"{e.amount}",
                created_by,
            ])
        return response
    except Exception as exc:
        # Log and show a friendly message if CSV generation fails in production
        messages.error(request, 'Failed to export expenditures as CSV. Please try again or contact support.')
        return redirect('expenditures_list')


def expenditures_export_pdf(request):
    """Export filtered expenditures as PDF using ReportLab. Falls back to a friendly message if ReportLab missing."""
    if not REPORTLAB_AVAILABLE:
        messages.error(request, 'PDF export requires the ReportLab package. Install it with `pip install reportlab`.')
        return redirect('expenditures_list')

    expenditures = Expenditure.objects.all().order_by('-expense_date')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date in (None, '', 'None'):
        start_date = None
    if end_date in (None, '', 'None'):
        end_date = None
    if start_date:
        expenditures = expenditures.filter(expense_date__date__gte=start_date)
    if end_date:
        expenditures = expenditures.filter(expense_date__date__lte=end_date)

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margin = 20 * mm
    y = height - margin

    # Header
    p.setFont('Helvetica-Bold', 14)
    p.drawString(margin, y, 'Expenditures Report')
    y -= 10 * mm
    p.setFont('Helvetica', 10)

    # Table header
    p.drawString(margin, y, 'ID')
    p.drawString(margin + 20 * mm, y, 'Category')
    p.drawString(margin + 60 * mm, y, 'Date')
    p.drawString(margin + 100 * mm, y, 'Amount')
    p.drawString(margin + 130 * mm, y, 'Description')
    y -= 6 * mm

    for e in expenditures:
        if y < margin + 20 * mm:
            p.showPage()
            y = height - margin
        date_str = ''
        try:
            date_str = timezone.localtime(e.expense_date).strftime('%Y-%m-%d %H:%M')
        except Exception:
            date_str = str(e.expense_date)

        p.drawString(margin, y, str(e.id))
        p.drawString(margin + 20 * mm, y, e.get_category_display())
        p.drawString(margin + 60 * mm, y, date_str)
        p.drawString(margin + 100 * mm, y, f"{e.amount}")
        # description may be long — wrap rudimentarily
        desc = (e.description or '')[:80]
        p.drawString(margin + 130 * mm, y, desc)
        y -= 6 * mm

    p.showPage()
    p.save()
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="expenditures.pdf"'
    return response


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
    """Create a new debt. If an item and quantity are provided, reduce stock accordingly."""
    if request.method == 'POST':
        form = DebtForm(request.POST)
        if form.is_valid():
            debt = form.save(commit=False)
            # If an item is provided and amount left blank, auto-calc from item price
            if debt.item and (debt.amount is None or debt.amount == 0):
                debt.amount = (debt.item.unit_price or Decimal('0.00')) * debt.quantity
            # If an item is provided and the user entered the item unit price (not the total),
            # treat it as a per-unit price and multiply by the quantity to store the total debt.
            elif debt.item and debt.amount is not None:
                try:
                    unit_price = (debt.item.unit_price or Decimal('0.00'))
                    # If the entered amount equals the unit price, assume it's a per-unit value
                    if debt.amount == unit_price:
                        debt.amount = debt.amount * debt.quantity
                except Exception:
                    # If anything goes wrong with comparison, fall back to using the provided amount
                    pass
            # Reduce stock if item provided
            if debt.item:
                if debt.item.stock_quantity < debt.quantity:
                    form.add_error('quantity', 'Insufficient stock to create debt for this quantity.')
                    return render(request, 'tracker/debt_form.html', {'form': form})
                else:
                    # deduct stock
                    debt.item.stock_quantity -= debt.quantity
                    debt.item.save(update_fields=['stock_quantity'])
            debt.save()
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

            # Create a Sale corresponding to this payment so sales dashboards reflect payments received
            try:
                sale = Sale.objects.create(
                    customer=debt.customer,
                    total_amount=payment.amount,
                    payment_method='cash',
                    is_paid=True,
                    notes=f'Payment for Debt #{debt.pk}'
                )
                # Only link the created sale to the debt if the debt had no originating sale
                # (we don't want to overwrite an original sale that generated the debt)
                if not debt.sale:
                    debt.sale = sale
                    debt.save(update_fields=['sale'])
            except Exception:
                # Don't prevent the payment from being recorded if sale creation fails
                sale = None

            messages.success(request, 'Payment added successfully!')
            return redirect('debt_detail', pk=debt.pk)
    else:
        # GET - display empty payment form
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
    
    # Paginate
    page = request.GET.get('page')
    paginator = Paginator(customers, 20)
    page_obj = paginator.get_page(page)

    context = {
        'customers': page_obj,
        'search_query': search_query,
        'paginator': paginator,
        'page_obj': page_obj,
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
