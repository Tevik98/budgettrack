from datetime import timedelta
from getpass import getpass
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from tracking.models import Category, DEFAULT_CATEGORIES, Expense


class Command(BaseCommand):
    help = 'Create a new demo account with fictional expenses; prompts for a password.'

    def add_arguments(self, parser):
        parser.add_argument('--username', default='demo')

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()
        username = options['username']
        if User.objects.filter(username=username).exists():
            raise CommandError('Account exists. Choose another --username; no data was changed.')
        user = User(username=username)
        password = getpass('New demo password: ')
        if password != getpass('Confirm password: '):
            raise CommandError('Passwords do not match.')
        try:
            user.full_clean(exclude=['password'])
            validate_password(password, user)
        except ValidationError as exc:
            raise CommandError('; '.join(exc.messages)) from exc
        user.set_password(password)
        user.save()
        categories = {name: Category.objects.create(owner=user, name=name, is_default=True)
                      for name in DEFAULT_CATEGORIES}
        today = timezone.localdate()
        samples = [('Food', 4875, 'Weekly groceries'), ('Transportation', 2500, 'Transit pass'),
                   ('Food', 650, 'Coffee with a friend'), ('Entertainment', 1600, 'Movie night'),
                   ('Utilities', 5999, 'Internet'), ('Health', 1800, 'Pharmacy'),
                   ('Shopping', 3490, 'Desk supplies'), ('Housing', 95000, 'Monthly rent')]
        Expense.objects.bulk_create([
            Expense(owner=user, category=categories[name], amount_cents=cents,
                    description=description, date=today - timedelta(days=days))
            for days, (name, cents, description) in enumerate(samples)
        ])
        self.stdout.write(self.style.SUCCESS(f'Created {username} with 8 fictional expenses.'))
