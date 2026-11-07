from datetime import date
from decimal import Decimal
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import Client, TestCase
from django.urls import reverse
from .models import Category, Expense


class AccountTests(TestCase):
    def test_signup_seeds_categories_and_logs_in(self):
        response = self.client.post(reverse('signup'), {
            'username': 'newuser', 'password1': 'Sample-test-password-729!',
            'password2': 'Sample-test-password-729!',
        })
        self.assertRedirects(response, reverse('expense_list'))
        user = get_user_model().objects.get(username='newuser')
        self.assertEqual(Category.objects.filter(owner=user, is_default=True).count(), 8)
        self.assertTrue(user.check_password('Sample-test-password-729!'))
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def test_anonymous_pages_require_login(self):
        for url in ['/', '/expenses/add/', '/categories/', '/expenses/1/edit/', '/expenses/1/delete/']:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 302)

    def test_login_and_post_only_logout(self):
        user = get_user_model().objects.create_user('alice', password='Sample-test-password-729!')
        response = self.client.post(reverse('login'), {'username': user.username, 'password': 'wrong'})
        self.assertContains(response, 'Please enter a correct')
        self.client.post(reverse('login'), {'username': user.username, 'password': 'Sample-test-password-729!'})
        self.assertIn('_auth_user_id', self.client.session)
        self.assertEqual(self.client.get(reverse('logout')).status_code, 405)
        self.client.post(reverse('logout'))
        self.assertNotIn('_auth_user_id', self.client.session)


class ExpenseTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.alice = User.objects.create_user('alice', password='Sample-test-password-729!')
        self.bob = User.objects.create_user('bob', password='Sample-test-password-729!')
        self.food = Category.objects.create(owner=self.alice, name='Food')
        self.other = Category.objects.create(owner=self.alice, name='Other')
        self.bobs_category = Category.objects.create(owner=self.bob, name='Private Bob Category')
        self.bobs_expense = Expense.objects.create(owner=self.bob, category=self.bobs_category,
            amount_cents=2000, date=date(2026, 11, 1), description='Private Bob Expense')
        self.client.force_login(self.alice)

    def post_expense(self, **overrides):
        data = {'amount': '12.34', 'date': '2026-11-06', 'category': self.food.pk, 'description': 'Lunch'}
        data.update(overrides)
        return self.client.post(reverse('expense_add'), data)

    def test_create_edit_and_delete_updates_totals(self):
        self.assertEqual(self.post_expense().status_code, 302)
        expense = Expense.objects.get(owner=self.alice)
        self.assertEqual(expense.amount_cents, 1234)
        self.assertEqual(expense.amount, Decimal('12.34'))
        response = self.client.post(reverse('expense_edit', args=[expense.pk]), {
            'amount': '0.30', 'date': '2026-10-31', 'category': self.other.pk, 'description': 'Revised',
        })
        self.assertRedirects(response, '/?month=2026-10')
        self.assertEqual(self.client.get('/?month=2026-11').context['total'], Decimal('0'))
        self.assertEqual(self.client.get('/?month=2026-10').context['total'], Decimal('0.30'))
        url = reverse('expense_delete', args=[expense.pk])
        self.assertContains(self.client.get(url), 'Delete this expense?')
        self.assertTrue(Expense.objects.filter(pk=expense.pk).exists())
        self.client.post(url)
        self.assertFalse(Expense.objects.filter(pk=expense.pk).exists())
        self.assertEqual(self.client.get('/?month=2026-10').context['total'], Decimal('0'))

    def test_other_users_records_are_inaccessible(self):
        self.assertNotContains(self.client.get('/?month='), 'Private Bob Expense')
        self.assertNotContains(self.client.get(reverse('categories')), 'Private Bob Category')
        for action in ['expense_edit', 'expense_delete']:
            url = reverse(action, args=[self.bobs_expense.pk])
            self.assertEqual(self.client.get(url).status_code, 404)
            self.assertEqual(self.client.post(url, {'amount': '1.00'}).status_code, 404)
        self.bobs_expense.refresh_from_db()
        self.assertEqual(self.bobs_expense.amount_cents, 2000)
        response = self.post_expense(category=self.bobs_category.pk, owner=self.bob.pk)
        self.assertContains(response, 'Select a valid choice')
        self.assertFalse(Expense.objects.filter(owner=self.alice).exists())

    def test_owner_field_cannot_be_spoofed(self):
        self.post_expense(owner=self.bob.pk)
        self.assertEqual(Expense.objects.get(description='Lunch').owner, self.alice)

    def test_invalid_amounts_and_dates_keep_form_input(self):
        for amount in ['0', '-1', '1.001', 'NaN', 'Infinity', '100000000.00']:
            response = self.post_expense(amount=amount)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context['form'].errors)
            self.assertContains(response, 'Lunch')
        self.assertContains(self.post_expense(date='2026-02-30'), 'Enter a valid date')
        self.assertFalse(Expense.objects.filter(owner=self.alice).exists())

    def test_exact_totals_filters_and_invalid_filter(self):
        self.post_expense(amount='0.10')
        self.post_expense(amount='0.20')
        self.post_expense(amount='1.25', category=self.other.pk)
        self.post_expense(amount='5.00', date='2026-10-31')
        response = self.client.get(f'/?month=2026-11&category={self.food.pk}')
        self.assertEqual(response.context['total'], Decimal('0.30'))
        self.assertEqual(response.context['count'], 2)
        self.assertEqual(self.client.get('/?month=').context['total'], Decimal('6.55'))
        for query in ['month=bad', 'month=2026-13', f'category={self.bobs_category.pk}']:
            response = self.client.get('/?' + query)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context['count'], 0)
            self.assertTrue(response.context['filter_form'].errors)

    def test_pagination_totals_include_all_matching_records(self):
        Expense.objects.bulk_create([Expense(owner=self.alice, category=self.food,
            amount_cents=100, date=date(2026, 11, 1)) for _ in range(17)])
        response = self.client.get('/?month=2026-11&page=2')
        self.assertEqual(response.context['total'], Decimal('17'))
        self.assertEqual(len(response.context['page_obj']), 2)
        self.assertContains(response, 'month=2026-11')

    def test_category_creation_is_private_and_case_insensitive(self):
        self.assertRedirects(self.client.post(reverse('categories'), {'name': '  Pets  '}), reverse('categories'))
        self.assertFalse(Category.objects.get(owner=self.alice, name='Pets').is_default)
        self.assertContains(self.client.post(reverse('categories'), {'name': 'pEtS'}), 'already have a category')
        Category.objects.create(owner=self.bob, name='Pets')
        self.assertContains(self.client.get(reverse('expense_add')), 'Pets')

    def test_csrf_protects_mutations(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.alice)
        for url in [reverse('expense_add'), reverse('categories'), reverse('logout')]:
            self.assertEqual(client.post(url, {}).status_code, 403)

    def test_descriptions_are_escaped(self):
        self.post_expense(description='<script>alert(1)</script>')
        response = self.client.get('/?month=2026-11')
        self.assertNotContains(response, '<script>alert(1)</script>')
        self.assertContains(response, '&lt;script&gt;')


class DemoCommandTests(TestCase):
    @patch('tracking.management.commands.seed_demo.getpass', return_value='Sample-test-password-729!')
    def test_seed_creates_sample_records_without_overwriting(self, prompt):
        call_command('seed_demo', username='demo')
        self.assertEqual(Expense.objects.count(), 8)
        self.assertEqual(Category.objects.count(), 8)
        with self.assertRaises(CommandError):
            call_command('seed_demo', username='demo')
        self.assertEqual(Expense.objects.count(), 8)
