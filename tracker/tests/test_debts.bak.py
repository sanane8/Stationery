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

    def test_payment_creates_sale_and_reflects_in_sales(self):
        debt = Debt.objects.create(
            customer=self.customer,
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

    def test_payment_creates_sale_and_reflects_in_sales(self):
        debt = Debt.objects.create(
            customer=self.customer,
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



















































        self.assertTrue(Sale.objects.filter(total_amount=Decimal('150.00')).exists())        self.assertEqual(resp.status_code, 302)        resp = self.client.post(reverse('add_payment', args=[debt.pk]), data)        }            'notes': 'Payment of debt'            'payment_method': 'cash',            'amount': str(Decimal('150.00')),        data = {        self.client.force_login(self.user)        )            due_date='2030-01-01'            amount=Decimal('150.00'),            customer=self.customer,        debt = Debt.objects.create(    def test_payment_creates_sale_and_reflects_in_sales(self):        self.assertEqual(item.stock_quantity, 7)        item.refresh_from_db()        self.assertEqual(resp.status_code, 302)        resp = self.client.post(reverse('create_debt'), data)        }            'description': 'Debting items',            'due_date': '2030-01-01',            'amount': str(item.unit_price * 3),            'quantity': '3',            'item': str(item.pk),            'customer': str(self.customer.pk),        data = {        self.client.force_login(self.user)        )            stock_quantity=10, minimum_stock=2            unit_price=Decimal('100.00'), cost_price=Decimal('60.00'),            name='Pen', sku='P-001', category=self.cat,        item = StationeryItem.objects.create(    def test_debt_creation_reduces_stock(self):        self.customer = Customer.objects.create(name='Debtor')        self.user = User.objects.create_user('testuser', 't@example.com', 'pw')        self.cat = Category.objects.create(name='DebtCat')    def setUp(self):class DebtsTests(TestCase):from tracker.models import Category, StationeryItem, Customer, Debt, Salefrom django.contrib.auth.models import Userfrom django.urls import reversefrom decimal import Decimalfrom decimal import Decimal
from django.urls import reverse
from tracker.models import Category, StationeryItem, Customer, Debt, Sale
from django.utils import timezone
