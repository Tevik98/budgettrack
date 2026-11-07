from datetime import date
from decimal import Decimal

from django.db.models import Sum
from django.db.models.functions import TruncMonth

from .budgets import budget_summary
from .models import Category, Expense, MonthlyBudget


def dashboard_data(user, month):
    budget = MonthlyBudget.objects.filter(owner=user, month=month).first()
    summary = budget_summary(user, month, budget, Category.objects.filter(owner=user))
    expenses = Expense.objects.filter(owner=user, date__year=month.year, date__month=month.month)
    category_rows = sorted((row for row in summary['category_rows'] if row['spent']),
                           key=lambda row: (-row['spent'], row['category'].name))
    total = summary['overall']['spent']
    for row in category_rows:
        row['share'] = row['spent'] * 100 / total
        row['bar_percent'] = max(1, int(row['share']))

    # Integer month indices handle year boundaries without platform-specific date formatting.
    index = (month.year - 1) * 12 + month.month - 1
    months = [date(i // 12 + 1, i % 12 + 1, 1) for i in range(max(0, index - 5), index + 1)]
    history = Expense.objects.filter(owner=user, date__gte=months[0],
        date__year__lte=month.year).exclude(date__year=month.year, date__month__gt=month.month)
    totals = dict(history.order_by().annotate(period=TruncMonth('date')).values('period')
                  .annotate(total=Sum('amount_cents')).values_list('period', 'total'))
    peak = max(totals.values(), default=0)
    trend = [{
        'month': item, 'amount': Decimal(totals.get(item, 0)) / 100,
        'bar_percent': max(1, totals.get(item, 0) * 100 // peak) if totals.get(item, 0) else 0,
        'selected': item == month,
    } for item in months]
    return {
        **summary, 'budget': budget, 'category_rows': category_rows, 'trend': trend,
        'expense_count': expenses.count(),
        'recent_expenses': expenses.select_related('category')[:5],
    }
