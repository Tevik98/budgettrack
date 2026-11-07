from datetime import timedelta
from decimal import Decimal
from django.db.models import Sum
from .models import Expense, MonthlyBudget


def previous_budget(user, month):
    if month.year == 1 and month.month == 1:
        return None
    previous = (month - timedelta(days=1)).replace(day=1)
    return MonthlyBudget.objects.filter(owner=user, month=previous).first()


def spending_status(spent, limit):
    return {
        'spent': Decimal(spent) / 100,
        'limit': Decimal(limit) / 100 if limit is not None else None,
        'remaining': Decimal(limit - spent) / 100 if limit is not None else None,
        'over': limit is not None and spent > limit,
        'percent': min(100, spent * 100 // limit) if limit else (100 if spent else 0),
    }


def budget_summary(user, month, budget, categories):
    expenses = Expense.objects.filter(owner=user, date__year=month.year, date__month=month.month)
    totals = dict(expenses.order_by().values('category_id').annotate(total=Sum('amount_cents'))
                  .values_list('category_id', 'total'))
    limits = dict(budget.limits.values_list('category_id', 'amount_cents')) if budget else {}
    return {
        'overall': spending_status(sum(totals.values()), budget.amount_cents if budget else None),
        'category_rows': [dict(category=category, **spending_status(
            totals.get(category.pk, 0), limits.get(category.pk))) for category in categories],
    }
