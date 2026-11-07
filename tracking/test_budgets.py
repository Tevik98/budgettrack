from datetime import date
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from .models import Category, CategoryLimit, Expense, MonthlyBudget


class BudgetTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user('planner')
        self.other = get_user_model().objects.create_user('other')
        self.category = Category.objects.create(owner=self.user, name='Food')
        self.foreign = Category.objects.create(owner=self.other, name='Private category')
        self.client.force_login(self.user)

    def save_budget(self, month='2026-11', overall='100.00', limit='25.00', **extra):
        return self.client.post('/budgets/?month=' + month,
            {'overall': overall, f'category_{self.category.pk}': limit, **extra})

    def test_create_and_update_exact_values(self):
        self.assertRedirects(self.save_budget(overall='100.30', limit='0.10'), '/budgets/?month=2026-11')
        budget = MonthlyBudget.objects.get(owner=self.user)
        self.assertEqual(budget.amount_cents, 10030)
        self.assertEqual(budget.limits.get().amount_cents, 10)
        self.save_budget(limit='')
        self.assertEqual(MonthlyBudget.objects.count(), 1)
        self.assertFalse(budget.limits.exists())

    def test_copy_previous_month_without_get_mutation_or_linked_edits(self):
        self.save_budget(month='2026-12', overall='100.30', limit='12.34')
        response = self.client.get('/budgets/?month=2027-01')
        self.assertEqual(response.context['form'].initial['overall'], Decimal('100.30'))
        self.assertEqual(response.context['form'].initial[f'category_{self.category.pk}'], Decimal('12.34'))
        self.assertIsNone(response.context['budget'])
        self.assertEqual(MonthlyBudget.objects.count(), 1)
        self.save_budget(month='2027-01', overall='100.30', limit='12.34')
        self.save_budget(month='2026-12', overall='999.00', limit='5.00')
        january = MonthlyBudget.objects.get(month=date(2027, 1, 1))
        self.assertEqual(january.amount_cents, 10030)
        self.assertEqual(january.limits.get().amount_cents, 1234)
        self.assertFalse(self.client.get('/budgets/?month=2027-03').context['form'].initial)

    def test_live_spending_and_overspending(self):
        self.save_budget(overall='0.30', limit='0.20')
        Expense.objects.create(owner=self.user, category=self.category, amount_cents=40, date=date(2026,11,1))
        Expense.objects.create(owner=self.user, category=self.category, amount_cents=900, date=date(2026,10,31))
        Expense.objects.create(owner=self.other, category=self.foreign, amount_cents=900, date=date(2026,11,1))
        response = self.client.get('/budgets/?month=2026-11')
        self.assertEqual(response.context['overall']['remaining'], Decimal('-0.10'))
        self.assertEqual(response.context['category_rows'][0]['remaining'], Decimal('-0.20'))
        self.assertContains(response, 'Over budget')
        expense = Expense.objects.get(owner=self.user, amount_cents=40)
        self.client.post(f'/expenses/{expense.pk}/edit/', {'amount':'0.10', 'date':'2026-11-01',
            'category': self.category.pk, 'description':'Updated'})
        self.assertEqual(self.client.get('/budgets/?month=2026-11').context['overall']['remaining'], Decimal('0.20'))
        self.client.post(f'/expenses/{expense.pk}/delete/')
        self.assertEqual(self.client.get('/budgets/?month=2026-11').context['overall']['remaining'], Decimal('0.30'))

    def test_zero_and_unset_are_distinct(self):
        response = self.client.get('/budgets/?month=2026-11')
        self.assertIsNone(response.context['overall']['remaining'])
        self.save_budget(overall='0', limit='0')
        response = self.client.get('/budgets/?month=2026-11')
        self.assertEqual(response.context['overall']['remaining'], Decimal('0'))
        self.assertEqual(response.context['category_rows'][0]['limit'], Decimal('0'))
        Expense.objects.create(owner=self.user, category=self.category, amount_cents=1, date=date(2026,11,1))
        self.assertTrue(self.client.get('/budgets/?month=2026-11').context['overall']['over'])

    def test_bad_input_is_not_saved(self):
        self.save_budget()
        for value in ['-1', '1.001', 'NaN', 'Infinity', '100000000.00', '']:
            response = self.save_budget(overall=value)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context['form'].errors)
        self.assertTrue(self.save_budget(limit='-1').context['form'].errors)
        self.assertEqual(MonthlyBudget.objects.get().amount_cents, 10000)
        self.assertEqual(CategoryLimit.objects.get().amount_cents, 2500)
        for month in ['bad', '2026-13', '', '2026-11-06']:
            self.assertEqual(self.client.get('/budgets/?month='+month).status_code, 400)
            self.assertEqual(self.save_budget(month=month).status_code, 400)
        self.assertEqual(MonthlyBudget.objects.count(), 1)

    def test_ownership_and_csrf(self):
        foreign_budget = MonthlyBudget.objects.create(owner=self.other, month=date(2026,11,1), amount_cents=123456)
        CategoryLimit.objects.create(budget=foreign_budget, category=self.foreign, amount_cents=100)
        response = self.client.get('/budgets/?month=2026-11')
        self.assertNotContains(response, 'Private category')
        self.assertIsNone(response.context['budget'])
        self.save_budget(**{'owner':self.other.pk, 'budget':foreign_budget.pk, f'category_{self.foreign.pk}':'999'})
        foreign_budget.refresh_from_db()
        self.assertEqual(foreign_budget.amount_cents, 123456)
        self.assertFalse(CategoryLimit.objects.filter(budget__owner=self.user, category=self.foreign).exists())
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        self.assertEqual(client.post('/budgets/?month=2026-11', {'overall':'1'}).status_code,403)
        self.client.logout()
        self.assertEqual(self.client.get('/budgets/').status_code,302)

    def test_new_category_gets_no_limit_and_overspending_does_not_block_expenses(self):
        self.save_budget(overall='0', limit='0')
        category = Category.objects.create(owner=self.user, name='Travel')
        response = self.client.get('/budgets/?month=2026-11')
        row = next(row for row in response.context['category_rows'] if row['category'] == category)
        self.assertIsNone(row['limit'])
        response = self.client.post('/expenses/add/', {'amount':'10.00', 'date':'2026-11-06',
            'category': category.pk, 'description': 'Allowed over budget'})
        self.assertEqual(response.status_code,302)
