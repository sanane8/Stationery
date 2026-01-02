from django.test import TestCase
from decimal import Decimal

from tracker.models import Category, StationeryItem, Sale, SaleItem


class StockRestoreTests(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(name='General')

    def test_sale_instance_delete_restores_stock(self):
        item = StationeryItem.objects.create(
            name='Pen',
            sku='PEN-001',
            category=self.cat,
            unit_price=Decimal('100.00'),
            cost_price=Decimal('50.00'),
            stock_quantity=10,
            minimum_stock=1,
        )

        sale = Sale.objects.create(total_amount=Decimal('0.00'))

        sale_item = SaleItem.objects.create(sale=sale, item=item, quantity=3, unit_price=item.unit_price)

        # stock reduced
        item.refresh_from_db()
        self.assertEqual(item.stock_quantity, 7)

        # delete the sale (which cascades)
        sale.delete()

        # stock restored
        item.refresh_from_db()
        self.assertEqual(item.stock_quantity, 10)

    def test_bulk_delete_restores_stock(self):
        item = StationeryItem.objects.create(
            name='Pencil',
            sku='PENCL-001',
            category=self.cat,
            unit_price=Decimal('50.00'),
            cost_price=Decimal('20.00'),
            stock_quantity=20,
            minimum_stock=1,
        )

        sale1 = Sale.objects.create(total_amount=Decimal('0.00'))
        sale2 = Sale.objects.create(total_amount=Decimal('0.00'))

        SaleItem.objects.create(sale=sale1, item=item, quantity=4, unit_price=item.unit_price)
        SaleItem.objects.create(sale=sale2, item=item, quantity=2, unit_price=item.unit_price)

        # stock reduced by total 6
        item.refresh_from_db()
        self.assertEqual(item.stock_quantity, 14)

        # bulk delete sales (using queryset delete)
        Sale.objects.filter(id__in=[sale1.id, sale2.id]).delete()

        # stock restored to original
        item.refresh_from_db()
        self.assertEqual(item.stock_quantity, 20)
