from django.test import TestCase
from decimal import Decimal
from django.urls import reverse
from django.contrib.auth.models import User
from tracker.models import Category, StationeryItem, Customer, Debt, Sale


class DebtsTests(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(name='DebtCat')
        self.user = User.objects.create_user('testuser', 't@example.com', 'pw')
        self.customer = Customer.objects.create(name='Debtor')

    def test_debt_creation_reduces_stock(self):
        item = StationeryItem.objects.create(
            name='Pen', sku='P-001', category=self.cat,
            unit_price=Decimal('100.00'), cost_price=Decimal('60.00'),
            stock_quantity=10, minimum_stock=2
        )
        self.client.force_login(self.user)
        data = {
            'customer': str(self.customer.pk),
            'item': str(item.pk),
            'quantity': '3',
            'amount': str(item.unit_price * 3),
            'due_date': '2030-01-01',
            'description': 'Debting items',
        }
        resp = self.client.post(reverse('create_debt'), data)
        self.assertEqual(resp.status_code, 302)
        item.refresh_from_db()
        self.assertEqual(item.stock_quantity, 7)

    def test_debt_creation_with_unit_price_input_multiplies_by_quantity(self):
        """If the user types the unit price in the amount field and provides a quantity,
        the stored debt amount should be (unit_price * quantity) rather than the unit price alone."""
        item = StationeryItem.objects.create(
            name='Pencil', sku='P-002', category=self.cat,
            unit_price=Decimal('500.00'), cost_price=Decimal('300.00'),
            stock_quantity=10, minimum_stock=2
        )
        self.client.force_login(self.user)
        data = {
            'customer': str(self.customer.pk),
            'item': str(item.pk),
            'quantity': '3',
            # simulate user entering the per-unit amount (500) expecting total = 1500
            'amount': str(item.unit_price),
            'due_date': '2030-01-01',
            'description': 'Debting items',
        }
        resp = self.client.post(reverse('create_debt'), data)
        self.assertEqual(resp.status_code, 302)
        debt = Debt.objects.order_by('-pk').first()
        self.assertIsNotNone(debt)
        self.assertEqual(debt.amount, item.unit_price * debt.quantity)
    def test_payment_creates_sale_and_reflects_in_sales(self):
        item = StationeryItem.objects.create(
            name='Eraser', sku='ER-001', category=self.cat,
            unit_price=Decimal('150.00'), cost_price=Decimal('80.00'),
            stock_quantity=10, minimum_stock=2
        )
        debt = Debt.objects.create(
            customer=self.customer,
            item=item,
            quantity=1,
            amount=Decimal('150.00'),
            due_date='2030-01-01'
        )
        self.client.force_login(self.user)
        data = {
            'amount': str(Decimal('150.00')),
            'payment_method': 'cash',
            'notes': 'Payment of debt'
        }
        resp = self.client.post(reverse('add_payment', args=[debt.pk]), data)
        self.assertEqual(resp.status_code, 302)
        # There should be a sale created for the payment amount
        self.assertTrue(Sale.objects.filter(total_amount=Decimal('150.00')).exists())
        debt.refresh_from_db()
        self.assertIsNotNone(debt.sale)
        self.assertEqual(debt.sale.total_amount, Decimal('150.00'))

    def test_payment_reflected_on_dashboard(self):
        item = StationeryItem.objects.create(
            name='Ruler', sku='RL-001', category=self.cat,
            unit_price=Decimal('75.00'), cost_price=Decimal('40.00'),
            stock_quantity=10, minimum_stock=2
        )
        debt = Debt.objects.create(
            customer=self.customer,
            item=item,
            quantity=1,
            amount=Decimal('75.00'),
            due_date='2030-01-01'
        )
        self.client.force_login(self.user)
        data = {
            'amount': str(Decimal('75.00')),
            'payment_method': 'cash',
            'notes': 'Debt payment'
        }
        resp = self.client.post(reverse('add_payment', args=[debt.pk]), data)
        self.assertEqual(resp.status_code, 302)
        # Dashboard should include this payment as today's sale (no expenditures to subtract)
        resp_dash = self.client.get(reverse('dashboard'))
        self.assertEqual(resp_dash.status_code, 200)
        self.assertGreaterEqual(resp_dash.context['net_today_sales'], Decimal('75.00'))

    def test_payment_sale_profit_proportional(self):
        # Create a sale that generates a debt (unpaid sale)
        item = StationeryItem.objects.create(
            name='Bundle', sku='BND-001', category=self.cat,
            unit_price=Decimal('100.00'), cost_price=Decimal('60.00'),
            stock_quantity=10, minimum_stock=1
        )
        sale = Sale.objects.create(total_amount=Decimal('0.00'), customer=self.customer, is_paid=False)
        from tracker.models import SaleItem
        SaleItem.objects.create(sale=sale, item=item, quantity=2, unit_price=item.unit_price)
        sale.refresh_from_db()
        # Original sale profit = (200 - 120) = 80
        orig_profit = sale.profit
        self.assertEqual(orig_profit, Decimal('80.00'))

        # There should be an auto-created debt pointing to this sale
        debt = Debt.objects.filter(sale=sale).first()
        self.assertIsNotNone(debt)
        self.client.force_login(self.user)

        # Make a partial payment of 100 (half of 200) via the view
        data = {'amount': str(Decimal('100.00')), 'payment_method': 'cash', 'notes': 'Partial payment'}
        resp = self.client.post(reverse('add_payment', args=[debt.pk]), data)
        self.assertEqual(resp.status_code, 302)

        # Find the created payment sale (notes have 'Payment for Debt #...')
        payment_sale = Sale.objects.filter(notes__contains=f'Payment for Debt #{debt.pk}').exclude(pk=sale.pk).first()
        self.assertIsNotNone(payment_sale)
        # Payment sale amount should be 100
        self.assertEqual(payment_sale.total_amount, Decimal('100.00'))
        # Expected profit = orig_profit * (100/200) = 40
        expected = (orig_profit * (Decimal('100.00') / debt.amount))
        # Compare decimals (allowing quantization differences)
        self.assertAlmostEqual(float(payment_sale.profit), float(expected), places=6)

    def test_payment_sale_shows_proportional_profit_in_sales_list(self):
        # Ensure the sales_list view exposes the proportional profit for payment-sales
        item = StationeryItem.objects.create(
            name='Bundle2', sku='BND-002', category=self.cat,
            unit_price=Decimal('100.00'), cost_price=Decimal('60.00'),
            stock_quantity=10, minimum_stock=1
        )
        orig_sale = Sale.objects.create(total_amount=Decimal('0.00'), customer=self.customer, is_paid=False)
        from tracker.models import SaleItem
        SaleItem.objects.create(sale=orig_sale, item=item, quantity=2, unit_price=item.unit_price)
        orig_sale.refresh_from_db()
        debt = Debt.objects.filter(sale=orig_sale).first()
        self.client.force_login(self.user)

        # Make a partial payment of 50 (quarter)
        data = {'amount': str(Decimal('50.00')), 'payment_method': 'cash', 'notes': 'Partial payment'}
        resp = self.client.post(reverse('add_payment', args=[debt.pk]), data)
        self.assertEqual(resp.status_code, 302)

        # Request sales list (default shows paid sales) and find payment sale
        resp2 = self.client.get(reverse('sales_list'))
        sales_list = list(resp2.context['sales'].object_list)
        payment_sale = None
        for s in sales_list:
            if f'Payment for Debt #{debt.pk}' in (s.notes or ''):
                payment_sale = s
                break
        self.assertIsNotNone(payment_sale, 'Payment sale not found in sales_list')
        # Expected proportional profit = orig_profit * (50 / debt.amount)
        expected = float(orig_sale.profit * (Decimal('50.00') / debt.amount))
        self.assertAlmostEqual(float(payment_sale.annotated_profit), expected, places=6)

        # Now make a final payment for the remaining amount and check proportional profits
        remaining = debt.amount - Decimal('50.00')
        data2 = {'amount': str(remaining), 'payment_method': 'cash', 'notes': 'Final payment'}
        resp2 = self.client.post(reverse('add_payment', args=[debt.pk]), data2)
        self.assertEqual(resp2.status_code, 302)
        payment_sale_final = Sale.objects.filter(notes__contains=f'Payment for Debt #{debt.pk}').exclude(pk=orig_sale.pk).order_by('-pk').first()
        self.assertIsNotNone(payment_sale_final)
        # For each payment, profit should be proportional to the payment amount
        orig_profit = orig_sale.profit
        final_expected = (orig_profit * (payment_sale_final.total_amount / debt.amount))
        self.assertAlmostEqual(float(payment_sale_final.profit), float(final_expected), places=6)

    def test_unpaid_sale_creates_debt(self):
        # Create a sale with a customer and add items -> should create an auto Debt
        item = StationeryItem.objects.create(
            name='Notebook', sku='NB-001', category=self.cat,
            unit_price=Decimal('200.00'), cost_price=Decimal('120.00'),
            stock_quantity=10, minimum_stock=1
        )
        # Sale initially unpaid
        sale = Sale.objects.create(total_amount=Decimal('0.00'), customer=self.customer, is_paid=False)
        # Add items to trigger total update and debt creation
        from tracker.models import SaleItem
        SaleItem.objects.create(sale=sale, item=item, quantity=2, unit_price=item.unit_price)
        # Refresh and check debt
        sale.refresh_from_db()
        d = Debt.objects.filter(sale=sale).first()
        self.assertIsNotNone(d)
        self.assertEqual(d.amount, sale.total_amount)
        self.assertEqual(d.status, 'pending')

    def test_unpaid_sale_via_views_appears_in_debt_list_and_has_correct_due_date(self):
        # Create sale via HTTP views, add an item, then ensure debt appears in debts list with correct due_date
        from django.utils import timezone
        from datetime import timedelta
        self.client.force_login(self.user)

        item = StationeryItem.objects.create(
            name='Glue', sku='GL-001', category=self.cat,
            unit_price=Decimal('50.00'), cost_price=Decimal('30.00'),
            stock_quantity=10, minimum_stock=1
        )

        # Create sale using the create_sale view with is_paid omitted (simulate unpaid)
        data = {'customer': str(self.customer.pk), 'payment_method': 'cash', 'notes': 'Unpaid via view'}
        resp = self.client.post(reverse('create_sale'), data)
        self.assertEqual(resp.status_code, 302)
        # Get the sale that was created
        sale = Sale.objects.order_by('-pk').first()
        self.assertFalse(sale.is_paid)

        # Add a sale item via the add_sale_item view (post)
        add_data = {
            'item': str(item.pk),
            'quantity': '2',
            'unit_price': str(item.unit_price),
            'total_price': str(item.unit_price * 2)
        }
        resp2 = self.client.post(reverse('add_sale_item', args=[sale.pk]), add_data)
        self.assertEqual(resp2.status_code, 302)

        # Fetch debts list and ensure the debt exists and shows up in response
        resp3 = self.client.get(reverse('debts_list'))
        self.assertEqual(resp3.status_code, 200)
        self.assertContains(resp3, self.customer.name)
        # Verify debt and its due_date
        d = Debt.objects.filter(sale=sale).first()
        self.assertIsNotNone(d)
        expected_due = timezone.localtime(sale.sale_date).date() + timedelta(days=7)
        self.assertEqual(d.due_date, expected_due)
        # Also assert the formatted due date appears in the rendered page
        self.assertContains(resp3, expected_due.strftime('%b %d, %Y'))

    def test_debt_due_date_uses_local_sale_date_to_avoid_off_by_one(self):
        # Simulate a sale created late at night in UTC that should be next-day in a local timezone
        from django.test.utils import override_settings
        from django.utils import timezone
        from datetime import timedelta
        tz_name = 'Africa/Dar_es_Salaam'  # UTC+3

        with override_settings(TIME_ZONE=tz_name):
            # Create a timezone-aware UTC datetime that is near midnight UTC and would shift date in local tz
            import datetime as _dt
            late_utc_dt = timezone.make_aware(timezone.datetime(2025, 12, 22, 23, 30, 0), _dt.timezone.utc)

            # Create sale with that UTC datetime
            sale = Sale.objects.create(total_amount=Decimal('0.00'), customer=self.customer, is_paid=False)
            sale.sale_date = late_utc_dt
            sale.save(update_fields=['sale_date'])

            # Add an item to ensure debt creation
            item = StationeryItem.objects.create(
                name='Marker', sku='MK-001', category=self.cat,
                unit_price=Decimal('100.00'), cost_price=Decimal('70.00'),
                stock_quantity=10, minimum_stock=1
            )
            from tracker.models import SaleItem
            SaleItem.objects.create(sale=sale, item=item, quantity=1, unit_price=item.unit_price)
            sale.refresh_from_db()

            d = Debt.objects.filter(sale=sale).first()
            self.assertIsNotNone(d)
            # Expected due date should be based on the local date (UTC+3 shifts 2025-12-22 23:30 -> 2025-12-23 local)
            expected_local_date = timezone.localtime(sale.sale_date).date()
            expected_due = expected_local_date + timedelta(days=7)
            self.assertEqual(d.due_date, expected_due)

    def test_marking_sale_paid_updates_debt(self):
        item = StationeryItem.objects.create(
            name='Pencil', sku='PC-001', category=self.cat,
            unit_price=Decimal('50.00'), cost_price=Decimal('20.00'),
            stock_quantity=10, minimum_stock=1
        )
        sale = Sale.objects.create(total_amount=Decimal('0.00'), customer=self.customer, is_paid=False)
        from tracker.models import SaleItem
        SaleItem.objects.create(sale=sale, item=item, quantity=3, unit_price=item.unit_price)
        sale.refresh_from_db()
        d = Debt.objects.filter(sale=sale).first()
        self.assertIsNotNone(d)
        # Now mark sale as paid
        sale.is_paid = True
        sale.save()
        d.refresh_from_db()
        self.assertEqual(d.status, 'paid')
        self.assertEqual(d.paid_amount, d.amount)

    def test_sale_without_customer_does_not_create_debt(self):
        item = StationeryItem.objects.create(
            name='Eraser', sku='ER-001', category=self.cat,
            unit_price=Decimal('30.00'), cost_price=Decimal('10.00'),
            stock_quantity=10, minimum_stock=1
        )
        sale = Sale.objects.create(total_amount=Decimal('0.00'), customer=None, is_paid=False)
        from tracker.models import SaleItem
        SaleItem.objects.create(sale=sale, item=item, quantity=1, unit_price=item.unit_price)
        sale.refresh_from_db()
        self.assertFalse(Debt.objects.filter(sale=sale).exists())

    def test_debt_due_date_is_based_on_sale_date(self):
        # Create a sale with an explicit sale_date and ensure the auto-created debt's due_date
        # is sale_date + 30 days
        from django.utils import timezone
        from datetime import timedelta
        item = StationeryItem.objects.create(
            name='Planner', sku='PL-001', category=self.cat,
            unit_price=Decimal('500.00'), cost_price=Decimal('300.00'),
            stock_quantity=10, minimum_stock=1
        )
        sale_date = timezone.now() - timedelta(days=5)
        # Create sale, set the sale_date explicitly, then create the sale item
        sale = Sale.objects.create(total_amount=Decimal('0.00'), customer=self.customer, is_paid=False)
        sale.sale_date = sale_date
        sale.save(update_fields=['sale_date'])
        from tracker.models import SaleItem
        SaleItem.objects.create(sale=sale, item=item, quantity=1, unit_price=item.unit_price)
        sale.refresh_from_db()
        d = Debt.objects.filter(sale=sale).first()
        self.assertIsNotNone(d)
        # The due_date uses the sale's local date to avoid timezone issues
        expected_due = (timezone.localtime(sale.sale_date).date() + timedelta(days=7))
        self.assertEqual(d.due_date, expected_due)

    def test_fix_auto_debt_due_dates_backfills_old_records(self):
        # Create a sale and an auto-created debt with a wrong due_date, run the management command and assert it's fixed
        from django.core.management import call_command
        from django.utils import timezone
        from datetime import timedelta

        sale = Sale.objects.create(total_amount=Decimal('0.00'), customer=self.customer, is_paid=False)
        # Set sale_date explicitly to a known date
        import datetime as _dt
        sale_date = timezone.make_aware(timezone.datetime(2025, 12, 10, 12, 0, 0), _dt.timezone.utc)
        sale.sale_date = sale_date
        sale.save(update_fields=['sale_date'])

        # Create an auto-created debt with a wrong due date
        wrong_due = (sale_date.date() + timedelta(days=5))
        # Provide an item so the legacy/incorrect auto-created debt still has an item assigned
        item = StationeryItem.objects.create(
            name='Temp', sku='TMP-001', category=self.cat,
            unit_price=Decimal('100.00'), cost_price=Decimal('50.00'),
            stock_quantity=0, minimum_stock=0
        )
        Debt.objects.create(customer=self.customer, sale=sale, item=item, quantity=1, amount=Decimal('100.00'), paid_amount=Decimal('0.00'), due_date=wrong_due, description=f'Auto-created from sale #{sale.pk}')

        # Run management command
        call_command('fix_auto_debt_due_dates')

        d = Debt.objects.get(sale=sale)
        expected = timezone.localtime(sale.sale_date).date() + timedelta(days=7)
        self.assertEqual(d.due_date, expected)
