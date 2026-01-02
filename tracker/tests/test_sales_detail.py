from django.test import TestCase
from decimal import Decimal
from django.urls import reverse
from tracker.models import Category, StationeryItem, Sale, SaleItem

class SaleDetailTests(TestCase):
    def setUp(self):
        cat = Category.objects.create(name='S')
        item = StationeryItem.objects.create(name='I', sku='S-1', category=cat, unit_price=Decimal('100'), cost_price=Decimal('60'), stock_quantity=10)
        sale = Sale.objects.create(total_amount=Decimal('100'))
        SaleItem.objects.create(sale=sale, item=item, quantity=1, unit_price=item.unit_price, total_price=item.unit_price)
        self.sale = sale

    def test_sale_detail_handles_missing_created_by(self):
        resp = self.client.get(reverse('sale_detail', args=[self.sale.pk]))
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode('utf-8')
        self.assertIn('<td>-</td>', content)
