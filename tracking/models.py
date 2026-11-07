from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.functions import Lower

DEFAULT_CATEGORIES = (
    'Food', 'Housing', 'Transportation', 'Utilities', 'Shopping',
    'Entertainment', 'Health', 'Other',
)


class MonthlyBudget(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    month = models.DateField(help_text='First day of the budget month.')
    amount_cents = models.PositiveBigIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['owner', 'month'], name='unique_owner_budget_month'),
            models.CheckConstraint(condition=models.Q(month__day=1), name='budget_month_first_day'),
        ]


class CategoryLimit(models.Model):
    budget = models.ForeignKey(MonthlyBudget, on_delete=models.CASCADE, related_name='limits')
    category = models.ForeignKey('Category', on_delete=models.PROTECT)
    amount_cents = models.PositiveBigIntegerField()

    class Meta:
        constraints = [models.UniqueConstraint(fields=['budget', 'category'], name='unique_budget_category')]

    def clean(self):
        if self.budget_id and self.category_id and self.budget.owner_id != self.category.owner_id:
            raise ValidationError({'category': 'Choose one of your own categories.'})


class Category(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=60)
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']
        constraints = [models.UniqueConstraint(
            Lower('name'), 'owner', name='unique_category_name_per_owner',
        )]

    def __str__(self):
        return self.name


class Expense(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    amount_cents = models.PositiveBigIntegerField()
    date = models.DateField()
    description = models.CharField(max_length=240, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-pk']
        constraints = [models.CheckConstraint(
            condition=models.Q(amount_cents__gt=0), name='positive_expense_amount',
        )]
        indexes = [models.Index(fields=['owner', 'date'])]

    @property
    def amount(self):
        return Decimal(self.amount_cents) / 100

    def clean(self):
        if self.category_id and self.owner_id and self.category.owner_id != self.owner_id:
            raise ValidationError({'category': 'Choose one of your own categories.'})
