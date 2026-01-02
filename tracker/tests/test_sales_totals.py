from django.test import TestCase, TransactionTestCase
from decimal import Decimal
from django.utils import timezone
import time
from tracker.models import Category, StationeryItem, Sale, SaleItem


class SaleTotalsTests(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(name='General')

    def test_total_updates_on_saleitem_create_and_delete(self):
        item1 = StationeryItem.objects.create(
            name='Marker A',
            sku='MRK-001',
            category=self.cat,
            unit_price=Decimal('150.00'),
            cost_price=Decimal('100.00'),
            stock_quantity=10,
            minimum_stock=1,
        )
        item2 = StationeryItem.objects.create(
            name='Marker B',
            sku='MRK-002',
            category=self.cat,
            unit_price=Decimal('200.00'),
            cost_price=Decimal('120.00'),
            stock_quantity=10,
            minimum_stock=1,
        )

        sale = Sale.objects.create(total_amount=Decimal('0.00'))

        # Create first sale item
        si1 = SaleItem.objects.create(sale=sale, item=item1, quantity=2, unit_price=item1.unit_price)
        sale.refresh_from_db()
        self.assertEqual(sale.total_amount, Decimal('300.00'))

        # Create second sale item (different item)
        si2 = SaleItem.objects.create(sale=sale, item=item2, quantity=1, unit_price=item2.unit_price)
        sale.refresh_from_db()
        self.assertEqual(sale.total_amount, Decimal('500.00'))

        # Delete one item and ensure total updates
        si1.delete()
        sale.refresh_from_db()
        self.assertEqual(sale.total_amount, Decimal('200.00'))

    def test_dashboard_reflects_today_sales_total(self):
        from django.urls import reverse
        # create items and sale via model so signals compute totals
        item1 = StationeryItem.objects.create(
            name='Stapler',
            sku='STP-001',
            category=self.cat,
            unit_price=Decimal('100.00'),
            cost_price=Decimal('60.00'),
            stock_quantity=10,
            minimum_stock=1,
        )
        sale = Sale.objects.create(total_amount=Decimal('0.00'))
        SaleItem.objects.create(sale=sale, item=item1, quantity=3, unit_price=item1.unit_price)

        client = self.client
        resp = client.get(reverse('dashboard'))
        today_sales = resp.context['today_sales']
        self.assertEqual(today_sales['total_sales'], Decimal('300.00'))

    def test_sales_page_daily_total_matches_dashboard_today(self):
        from django.urls import reverse
        item = StationeryItem.objects.create(
            name='Glue',
            sku='GLU-001',
            category=self.cat,
            unit_price=Decimal('120.00'),
            cost_price=Decimal('80.00'),
            stock_quantity=10,
            minimum_stock=1,
        )
        sale = Sale.objects.create(total_amount=Decimal('0.00'))
        SaleItem.objects.create(sale=sale, item=item, quantity=2, unit_price=item.unit_price)

        client = self.client
        dash_resp = client.get(reverse('dashboard'))
        dash_total = dash_resp.context['today_sales']['total_sales'] or Decimal('0')

        # Request sales_list including unpaid sales so it matches the dashboard's "today_sales"
        # Request sales_list (defaults to paid sales) — should match dashboard's today totals
        sales_resp = client.get(reverse('sales_list'))
        # find today's entry in daily_sales list
        daily = sales_resp.context['daily_sales']
        today_date = timezone.localtime(timezone.now()).date()
        found = None
        for d in daily:
            if d['date'] == today_date:
                found = d
                break
        self.assertIsNotNone(found, f"No daily entry found for today ({today_date}) on sales page")
        self.assertEqual(found['revenue'], dash_total)

    def test_unpaid_sales_not_in_dashboard_recent_and_today(self):
        from django.urls import reverse
        # create an unpaid sale and ensure it's not counted in today's totals or recent list
        item = StationeryItem.objects.create(
            name='HiddenToday',
            sku='HT-001',
            category=self.cat,
            unit_price=Decimal('90.00'),
            cost_price=Decimal('50.00'),
            stock_quantity=10,
            minimum_stock=1,
        )
        unpaid_sale = Sale.objects.create(total_amount=Decimal('0.00'), is_paid=False)
        from tracker.models import SaleItem
        SaleItem.objects.create(sale=unpaid_sale, item=item, quantity=1, unit_price=item.unit_price)
        unpaid_sale.refresh_from_db()

        client = self.client
        dash_resp = client.get(reverse('dashboard'))
        today_total = dash_resp.context['today_sales']['total_sales'] or Decimal('0')
        # The unpaid sale amount should not be included in today's total
        self.assertNotEqual(today_total, unpaid_sale.total_amount)

        # Recent sales should not include the unpaid sale by default
        resp = client.get(reverse('dashboard'))
        recent = resp.context['recent_sales']
        ids = [s.id for s in recent]
        self.assertNotIn(unpaid_sale.id, ids)
    def test_unpaid_sales_not_in_monthly_totals(self):
        from django.urls import reverse
        # create a paid and an unpaid sale this month, ensure monthly totals include only paid sale
        item = StationeryItem.objects.create(
            name='MonthlyCheck',
            sku='MC-001',
            category=self.cat,
            unit_price=Decimal('100.00'),
            cost_price=Decimal('60.00'),
            stock_quantity=10,
            minimum_stock=1,
        )
        # Paid sale of 3 units => 300
        paid_sale = Sale.objects.create(total_amount=Decimal('0.00'), is_paid=True)
        from tracker.models import SaleItem
        SaleItem.objects.create(sale=paid_sale, item=item, quantity=3, unit_price=item.unit_price)
        # Unpaid sale of 2 units => 200
        unpaid_sale = Sale.objects.create(total_amount=Decimal('0.00'), is_paid=False)
        SaleItem.objects.create(sale=unpaid_sale, item=item, quantity=2, unit_price=item.unit_price)

        client = self.client
        resp = client.get(reverse('dashboard'))
        month_total = resp.context['net_monthly_sales'] or Decimal('0')
        self.assertEqual(month_total, Decimal('300.00'))
    def test_unpaid_sales_not_in_default_list(self):
        from django.urls import reverse
        from decimal import Decimal
        item = StationeryItem.objects.create(
            name='DefaultHide',
            sku='DH-001',
            category=self.cat,
            unit_price=Decimal('60.00'),
            cost_price=Decimal('30.00'),
            stock_quantity=10,
            minimum_stock=1,
        )
        sale = Sale.objects.create(total_amount=Decimal('0.00'), customer=None, is_paid=False)
        # add a sale item to make the sale visible (and to update totals)
        from tracker.models import SaleItem
        SaleItem.objects.create(sale=sale, item=item, quantity=1, unit_price=item.unit_price)

        # By default (no params) unpaid sales should NOT appear
        resp = self.client.get(reverse('sales_list'))
        shown_ids = [s.id for s in resp.context['sales'].object_list]
        self.assertNotIn(sale.id, shown_ids)

        # When requesting 'all' they should be visible
        resp_all = self.client.get(reverse('sales_list') + '?payment_status=all')
        shown_ids_all = [s.id for s in resp_all.context['sales'].object_list]
        self.assertIn(sale.id, shown_ids_all)

    def test_create_sale_requires_customer_when_unpaid(self):
        from django.urls import reverse
        # Attempt to create sale without customer and unpaid => should show validation error
        # Omit 'is_paid' from POST to simulate unchecked checkbox (which resolves to False)
        from django.contrib.auth.models import User
        user = User.objects.create_user(username='testuser1', password='pw')
        self.client.force_login(user)
        data = {'customer': '', 'payment_method': 'cash', 'notes': 'Test unpaid without customer'}
        resp = self.client.post(reverse('create_sale'), data)
        # Expect form re-render with errors (status 200) and no redirect
        self.assertEqual(resp.status_code, 200)
        # Check the form has an error for customer
        form = resp.context['form']
        self.assertTrue(form.errors)
        self.assertIn('customer', form.errors)

    def test_create_sale_allows_no_customer_when_paid(self):
        from django.urls import reverse
        data = {'customer': '', 'payment_method': 'cash', 'is_paid': 'on', 'notes': 'Paid no customer'}
        resp = self.client.post(reverse('create_sale'), data)
        # A redirect indicates success
        self.assertEqual(resp.status_code, 302)
        # Sale should have been created
        self.assertTrue(Sale.objects.filter(notes='Paid no customer').exists())

    def test_add_same_item_twice_increments_quantity(self):
        from django.urls import reverse
        from django.contrib.auth.models import User

        user = User.objects.create_user(username='testuser', password='pass')
        self.client.force_login(user)

        item = StationeryItem.objects.create(
            name='Tape',
            sku='TAP-001',
            category=self.cat,
            unit_price=Decimal('50.00'),
            cost_price=Decimal('30.00'),
            stock_quantity=10,
            minimum_stock=1,
        )
        sale = Sale.objects.create(total_amount=Decimal('0.00'))

        url = reverse('add_sale_item', kwargs={'sale_id': sale.pk})
        # first add
        resp1 = self.client.post(url, {'item': item.pk, 'quantity': 2, 'unit_price': str(item.unit_price)})
        self.assertEqual(resp1.status_code, 302)  # redirect to sale detail

        # second add of same item
        resp2 = self.client.post(url, {'item': item.pk, 'quantity': 3, 'unit_price': str(item.unit_price)})
        self.assertEqual(resp2.status_code, 302)

        sale.refresh_from_db()
        si = sale.items.get(item=item)
        self.assertEqual(si.quantity, 5)
        # stock reduced by 5
        item.refresh_from_db()
        self.assertEqual(item.stock_quantity, 5)
        # total amount should be 5 * 50 = 250
        self.assertEqual(sale.total_amount, Decimal('250.00'))


from django.test import override_settings


@override_settings(
    SESSION_ENGINE='django.contrib.sessions.backends.cache',
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
        }
    },
    MESSAGE_STORAGE='django.contrib.messages.storage.cookie.CookieStorage'
)
class ConcurrencyTests(TransactionTestCase):
    """Simulate concurrent adds to the same sale to ensure no UNIQUE errors and final totals are correct."""
    reset_sequences = True

    def setUp(self):
        self.cat = Category.objects.create(name='Concurrency')
        from django.contrib.auth.models import User
        self.user = User.objects.create_user(username='concurrent', password='pass')

    def test_concurrent_adds_to_same_sale(self):
        from django.urls import reverse
        from django.test import Client
        import threading

        item = StationeryItem.objects.create(
            name='Staple',
            sku='STP-999',
            category=self.cat,
            unit_price=Decimal('10.00'),
            cost_price=Decimal('5.00'),
            stock_quantity=100,
            minimum_stock=1,
        )
        sale = Sale.objects.create(total_amount=Decimal('0.00'))

        url = reverse('add_sale_item', kwargs={'sale_id': sale.pk})
        exceptions = []

        def worker(qty):
            import time
            max_attempts = 20
            for attempt in range(max_attempts):
                try:
                    c = Client()
                    c.force_login(self.user)
                    c.post(url, {'item': item.pk, 'quantity': qty, 'unit_price': str(item.unit_price)})
                    return
                except Exception as e:
                    # SQLite can produce 'database table is locked' under concurrency; retry with backoff
                    msg = str(e)
                    if 'database table is locked' in msg or 'database is locked' in msg:
                        if attempt < max_attempts - 1:
                            time.sleep(0.02 * (attempt + 1))
                            continue
                    exceptions.append(e)
                    return

        threads = []
        # Start 5 threads each adding quantity=2 => expected final quantity 10
        for i in range(5):
            t = threading.Thread(target=worker, args=(2,))
            threads.append(t)
            t.start()
            # slight stagger to reduce SQLITE lock contention
            time.sleep(0.02)

        for t in threads:
            t.join()

        # Ensure no thread threw an exception
        if exceptions:
            self.fail(f"Exceptions occurred during concurrent posts: {exceptions}")

        sale.refresh_from_db()
        item.refresh_from_db()
        si = sale.items.get(item=item)
        self.assertEqual(si.quantity, 10)
        self.assertEqual(item.stock_quantity, 90)
        self.assertEqual(sale.total_amount, Decimal('100.00'))
