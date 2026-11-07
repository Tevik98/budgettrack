from datetime import date
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from .models import Category, CategoryLimit, Expense, MonthlyBudget


class DashboardTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user('viewer')
        self.other = get_user_model().objects.create_user('outsider')
        self.food = Category.objects.create(owner=self.user, name='Food')
        self.travel = Category.objects.create(owner=self.user, name='Travel')
        self.client.force_login(self.user)

    def expense(self, cents, day, category=None, description='Example'):
        return Expense.objects.create(owner=self.user, category=category or self.food,
            amount_cents=cents, date=date.fromisoformat(day), description=description)

    def test_totals_categories_and_saved_budget_match(self):
        self.expense(10, '2026-11-01')
        self.expense(20, '2026-11-02')
        self.expense(70, '2026-11-03', self.travel)
        self.expense(5000, '2026-10-31')
        budget = MonthlyBudget.objects.create(owner=self.user, month=date(2026,11,1), amount_cents=90)
        CategoryLimit.objects.create(budget=budget, category=self.travel, amount_cents=60)
        response = self.client.get('/dashboard/?month=2026-11')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['overall']['spent'], Decimal('1.00'))
        self.assertEqual(response.context['overall']['remaining'], Decimal('-0.10'))
        self.assertEqual(response.context['expense_count'], 3)
        rows = response.context['category_rows']
        self.assertEqual(rows[0]['category'], self.travel)
        self.assertEqual(rows[0]['share'], Decimal('70'))
        self.assertEqual(rows[1]['spent'], Decimal('0.30'))
        self.assertContains(response, 'Over category limit')
        self.assertEqual(response.context['overall'], self.client.get('/budgets/?month=2026-11').context['overall'])

    def test_history_crosses_year_and_excludes_out_of_window(self):
        self.expense(100, '2025-08-01')
        self.expense(200, '2025-12-31')
        self.expense(300, '2026-01-01')
        self.expense(999, '2025-07-31')
        self.expense(999, '2026-02-01')
        trend = self.client.get('/dashboard/?month=2026-01').context['trend']
        self.assertEqual(len(trend), 6)
        self.assertEqual(trend[0]['month'], date(2025,8,1))
        self.assertEqual([row['amount'] for row in trend], list(map(Decimal, ['1','0','0','0','2','3'])))
        self.assertEqual(trend[-1]['bar_percent'], 100)

    def test_private_data_is_excluded_everywhere(self):
        category = Category.objects.create(owner=self.other, name='Secret category')
        Expense.objects.create(owner=self.other, category=category, date=date(2026,11,1), amount_cents=99999, description='Secret expense')
        MonthlyBudget.objects.create(owner=self.other, month=date(2026,11,1), amount_cents=99999)
        response = self.client.get('/dashboard/?month=2026-11&owner='+str(self.other.pk))
        self.assertNotContains(response, 'Secret')
        self.assertIsNone(response.context['budget'])
        self.assertEqual(response.context['overall']['spent'], 0)
        self.assertTrue(all(row['amount'] == 0 for row in response.context['trend']))
        self.assertFalse(response.context['recent_expenses'])

    def test_empty_zero_budget_and_no_get_mutation(self):
        response = self.client.get('/dashboard/?month=2026-11')
        self.assertContains(response, 'A fresh month')
        self.assertContains(response, 'Not set')
        self.assertIsNone(response.context['overall']['remaining'])
        self.assertFalse(MonthlyBudget.objects.exists())
        MonthlyBudget.objects.create(owner=self.user, month=date(2026,11,1), amount_cents=0)
        self.expense(1, '2026-11-01')
        response = self.client.get('/dashboard/?month=2026-11')
        self.assertTrue(response.context['overall']['over'])
        self.assertEqual(response.context['overall']['remaining'], Decimal('-0.01'))

    def test_recent_expenses_are_latest_five_in_selected_month(self):
        for day in range(1,8):
            self.expense(100, f'2026-11-{day:02d}')
        self.expense(100, '2026-12-01', description='Future expense')
        response = self.client.get('/dashboard/?month=2026-11')
        self.assertEqual([e.date.day for e in response.context['recent_expenses']], [7,6,5,4,3])
        self.assertEqual(response.context['expense_count'], 7)
        self.assertNotContains(response, 'Future expense')

    def test_updates_refresh_dashboard(self):
        expense = self.expense(100, '2026-11-01')
        self.client.post(f'/expenses/{expense.pk}/edit/', {'amount':'2.50','date':'2026-10-31','category':self.food.pk})
        response = self.client.get('/dashboard/?month=2026-11')
        self.assertEqual(response.context['overall']['spent'], 0)
        self.assertEqual(response.context['trend'][-2]['amount'], Decimal('2.50'))
        self.client.post(f'/expenses/{expense.pk}/delete/')
        self.assertEqual(self.client.get('/dashboard/?month=2026-11').context['trend'][-2]['amount'], 0)

    def test_invalid_month_authentication_and_html_escaping(self):
        for month in ['', 'bad', '2026-13', '2026-01-01']:
            self.assertEqual(self.client.get('/dashboard/?month='+month).status_code, 400)
        self.expense(100, '2026-11-01', description='<script>bad()</script>')
        self.assertContains(self.client.get('/dashboard/?month=2026-11'), '&lt;script&gt;')
        self.assertEqual(self.client.get('/dashboard/?month=0001-01').status_code, 200)
        self.assertEqual(self.client.get('/dashboard/?month=9999-12').status_code, 200)
        self.assertEqual(self.client.post('/dashboard/').status_code, 405)
        self.client.logout()
        self.assertEqual(self.client.get('/dashboard/').status_code, 302)
