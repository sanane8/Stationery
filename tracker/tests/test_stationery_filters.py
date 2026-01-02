from django.test import TestCase
from decimal import Decimal
from tracker.models import Category, StationeryItem
from django.urls import reverse


class StationeryFiltersTests(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(name='StationeryTest')

    def test_low_stock_filter(self):
        # low stock item
        low = StationeryItem.objects.create(
            name='LowPen', sku='LPN-001', category=self.cat,
            unit_price=Decimal('100.00'), cost_price=Decimal('60.00'),
            stock_quantity=1, minimum_stock=2
        )
        # healthy stock item
        ok = StationeryItem.objects.create(
            name='OkPen', sku='OKP-001', category=self.cat,
            unit_price=Decimal('120.00'), cost_price=Decimal('70.00'),
            stock_quantity=10, minimum_stock=2
        )

        client = self.client
        resp = client.get(reverse('stationery_list') + '?low_stock=1')
        self.assertEqual(resp.status_code, 200)
        items = resp.context['items'].object_list
        # only the low stock item should be present
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].pk, low.pk)
        # check context flags
        self.assertTrue(resp.context['selected_low_stock'])
        self.assertEqual(resp.context['low_stock_count'], 1)

    def test_low_stock_button_preserves_other_filters(self):
        # create items including one low-stock that matches search term
        low = StationeryItem.objects.create(
            name='FilterPen', sku='FLT-001', category=self.cat,
            unit_price=Decimal('90.00'), cost_price=Decimal('50.00'),
            stock_quantity=1, minimum_stock=2
        )
        other = StationeryItem.objects.create(
            name='OtherPen', sku='OTH-001', category=self.cat,
            unit_price=Decimal('110.00'), cost_price=Decimal('70.00'),
            stock_quantity=3, minimum_stock=2
        )

        client = self.client
        # When we have a search filter, the low-stock quick action should be available in the page actions
        resp_search = client.get(reverse('stationery_list') + '?search=Filter')
        content = resp_search.content.decode('utf-8')
        # page-action should add low_stock=1 to the url preserving other params
        self.assertIn('low_stock=1', content)

        # When we follow the page-action link, the resulting page should apply the low-stock filter while preserving search
        resp_toggle = client.get(reverse('stationery_list') + '?search=Filter&low_stock=1')
        items = resp_toggle.context['items'].object_list
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].pk, low.pk)

    def test_inactive_toggle_and_checkbox(self):
        # create one inactive and one active item
        inactive = StationeryItem.objects.create(
            name='InactivePen', sku='INACT-01', category=self.cat,
            unit_price=Decimal('80.00'), cost_price=Decimal('40.00'),
            stock_quantity=5, minimum_stock=2, is_active=False
        )
        active = StationeryItem.objects.create(
            name='ActivePen', sku='ACT-01', category=self.cat,
            unit_price=Decimal('95.00'), cost_price=Decimal('50.00'),
            stock_quantity=5, minimum_stock=2, is_active=True
        )

        client = self.client
        # Toggle via button link (should include search params when present)
        resp = client.get(reverse('stationery_list') + '?inactive=1')
        self.assertEqual(resp.status_code, 200)
        items = resp.context['items'].object_list
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].pk, inactive.pk)

        # Confirm checkbox rendering when active
        resp2 = client.get(reverse('stationery_list') + '?inactive=1&search=Active')
        html = resp2.content.decode('utf-8')
        self.assertIn('name="inactive" value="1" checked', html)
        # If both inactive and low_stock are present in query, both checkboxes should be checked
        resp3 = client.get(reverse('stationery_list') + '?inactive=1&low_stock=1')
        html2 = resp3.content.decode('utf-8')
        self.assertIn('name="inactive" value="1" checked', html2)
        self.assertIn('name="low_stock" value="1" checked', html2)
    def test_low_stock_after_inactive_toggle(self):
        # ensure low-stock toggle works after inactive toggle is applied
        low_inactive = StationeryItem.objects.create(
            name='LowInactive', sku='LINACT-01', category=self.cat,
            unit_price=Decimal('60.00'), cost_price=Decimal('30.00'),
            stock_quantity=1, minimum_stock=5, is_active=False
        )
        other_inactive = StationeryItem.objects.create(
            name='OtherInactive', sku='OINACT-01', category=self.cat,
            unit_price=Decimal('70.00'), cost_price=Decimal('40.00'),
            stock_quantity=10, minimum_stock=2, is_active=False
        )

        client = self.client
        # First, apply inactive toggle via page action
        resp_inactive = client.get(reverse('stationery_list') + '?inactive=1')
        self.assertEqual(resp_inactive.status_code, 200)
        items = resp_inactive.context['items'].object_list
        # we should see both inactive items
        self.assertTrue(any(item.pk == low_inactive.pk for item in items))
        self.assertTrue(any(item.pk == other_inactive.pk for item in items))

        # Now, click low-stock action while inactive toggle is still 'active'
        resp_both = client.get(reverse('stationery_list') + '?inactive=1&low_stock=1')
        self.assertEqual(resp_both.status_code, 200)
        items_both = resp_both.context['items'].object_list
        # only low_inactive should remain
        self.assertEqual(len(items_both), 1)
        self.assertEqual(items_both[0].pk, low_inactive.pk)

    def test_page_action_preserves_inactive_when_set_via_checkbox(self):
        # clicking the page-action low-stock button should preserve inactive when set via the checkbox
        low_inactive = StationeryItem.objects.create(
            name='LowInactive', sku='LINACT-02', category=self.cat,
            unit_price=Decimal('60.00'), cost_price=Decimal('30.00'),
            stock_quantity=1, minimum_stock=5, is_active=False
        )
        other_inactive = StationeryItem.objects.create(
            name='OtherInactive', sku='OINACT-02', category=self.cat,
            unit_price=Decimal('70.00'), cost_price=Decimal('40.00'),
            stock_quantity=10, minimum_stock=2, is_active=False
        )

        client = self.client
        # Simulate submitting the form with inactive checkbox checked (inactive=1)
        resp_checkbox = client.get(reverse('stationery_list') + '?inactive=1')
        self.assertEqual(resp_checkbox.status_code, 200)
        html = resp_checkbox.content.decode('utf-8')
        # The page-action link should preserve the inactive param and still include low-stock toggle
        self.assertIn('inactive=1', html)
        self.assertIn('low_stock=1', html)

        # Follow the low-stock quick-action link that preserves inactive
        resp_both = client.get(reverse('stationery_list') + '?inactive=1&low_stock=1')
        self.assertEqual(resp_both.status_code, 200)
        items_both = resp_both.context['items'].object_list
        # only low_inactive should remain
        self.assertEqual(len(items_both), 1)
        self.assertEqual(items_both[0].pk, low_inactive.pk)

    def test_page_action_toggle_buttons(self):
        # quick action buttons next to Add Item should exist and perform toggles
        low = StationeryItem.objects.create(
            name='ActionLow', sku='ACTLOW-01', category=self.cat,
            unit_price=Decimal('75.00'), cost_price=Decimal('40.00'),
            stock_quantity=1, minimum_stock=2
        )
        inactive = StationeryItem.objects.create(
            name='ActionInactive', sku='ACTIN-01', category=self.cat,
            unit_price=Decimal('85.00'), cost_price=Decimal('45.00'),
            stock_quantity=5, minimum_stock=2, is_active=False
        )

        client = self.client
        resp = client.get(reverse('stationery_list'))
        self.assertEqual(resp.status_code, 200)
        html = resp.content.decode('utf-8')
        # Quick-toggle links should be present in the page actions
        self.assertIn('low_stock=1', html)
        self.assertIn('inactive=1', html)

        # Following the low-stock quick action should apply the low-stock filter
        resp_low = client.get(reverse('stationery_list') + '?low_stock=1')
        items = resp_low.context['items'].object_list
        self.assertTrue(any(item.is_low_stock for item in items))

        # Following the inactive quick action should show only inactive items
        resp_inact = client.get(reverse('stationery_list') + '?inactive=1')
        items_inact = resp_inact.context['items'].object_list
        self.assertTrue(all(not item.is_active for item in items_inact))