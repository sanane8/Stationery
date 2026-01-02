from django.test import TestCase
from decimal import Decimal
from django.urls import reverse
from django.contrib.auth.models import User
from tracker.models import Category, Expenditure
from django.utils import timezone


class ExpenditureTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='pass')
        self.client.login(username='tester', password='pass')
        self.cat = Category.objects.create(name='General')

    def test_create_and_list_expenditure(self):
        resp = self.client.post(reverse('create_expenditure'), {
            'category': 'supplies',
            'description': 'Office paper',
            'amount': '5000.00',
            'expense_date': '2025-12-07T10:00',
        }, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Expenditure recorded successfully.')

        resp = self.client.get(reverse('expenditures_list'))
        self.assertContains(resp, 'Office paper')

    def test_export_csv(self):
        Expenditure.objects.create(category='rent', description='Shop rent', amount=Decimal('100000.00'))
        resp = self.client.get(reverse('expenditures_export'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'text/csv')

    def test_expenditure_reduces_dashboard_totals(self):
        # Create a sale for today and an expenditure for today and confirm dashboard shows net amount
        from tracker.models import Sale
        now = timezone.localtime(timezone.now())
        sale = Sale.objects.create(total_amount=Decimal('10000.00'))
        Expenditure.objects.create(category='supplies', description='Paper', amount=Decimal('2000.00'))

        resp = self.client.get(reverse('dashboard'))
        self.assertEqual(resp.status_code, 200)
        # net today sales should be sale - expenditure
        net = resp.context['net_today_sales']
        self.assertEqual(net, Decimal('8000.00'))
        self.assertEqual(resp.context['exp_today']['total'], Decimal('2000.00'))

    def test_expenditure_reduces_sales_list_totals(self):
        from tracker.models import Sale
        now = timezone.localtime(timezone.now())
        date_str = now.date().isoformat()
        sale = Sale.objects.create(total_amount=Decimal('50000.00'), sale_date=now)
        Expenditure.objects.create(category='other', description='Misc', amount=Decimal('5000.00'), expense_date=now)

        resp = self.client.get(reverse('sales_list') + f'?start_date={date_str}&end_date={date_str}')
        self.assertEqual(resp.status_code, 200)
        total_net = resp.context['total_amount_net']
        self.assertEqual(total_net, Decimal('45000.00'))
        # daily summary should reflect net revenue
        daily = resp.context['daily_sales']
        # find entry for today
        today_entry = next((d for d in daily if d['date'] == now.date()), None)
        self.assertIsNotNone(today_entry)
        self.assertEqual(today_entry['revenue'], Decimal('45000.00'))
