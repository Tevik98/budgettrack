from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .forms import BudgetForm, BudgetMonthForm, CategoryForm, ExpenseFilterForm, ExpenseForm
from .models import Category, CategoryLimit, DEFAULT_CATEGORIES, Expense, MonthlyBudget
from .budgets import budget_summary, previous_budget
from .dashboard import dashboard_data


@require_http_methods(['GET', 'POST'])
def signup(request):
    if request.user.is_authenticated:
        return redirect('expense_list')
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            user = form.save()
            Category.objects.bulk_create([
                Category(owner=user, name=name, is_default=True) for name in DEFAULT_CATEGORIES
            ])
        login(request, user)
        messages.success(request, 'Welcome to BudgetTrack. Add your first expense to get started.')
        return redirect('expense_list')
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def expense_list(request):
    params = request.GET.copy()
    if 'month' not in params:
        params['month'] = timezone.localdate().strftime('%Y-%m')
    form = ExpenseFilterForm(params, user=request.user)
    expenses = Expense.objects.filter(owner=request.user).select_related('category')
    period = 'All time'
    if form.is_valid():
        month = form.cleaned_data['month']
        if month:
            expenses = expenses.filter(date__year=month.year, date__month=month.month)
            period = month.strftime('%B %Y')
        if form.cleaned_data['category']:
            expenses = expenses.filter(category=form.cleaned_data['category'])
    else:
        expenses = expenses.none()
        period = 'Check your filters'
    total_cents = expenses.aggregate(total=Sum('amount_cents'))['total'] or 0
    paginator = Paginator(expenses, 15)
    page = paginator.get_page(request.GET.get('page'))
    params.pop('page', None)
    return render(request, 'tracking/expense_list.html', {
        'filter_form': form, 'page_obj': page, 'query': params.urlencode(),
        'total': Decimal(total_cents) / 100, 'count': paginator.count, 'period': period,
        'category_count': Category.objects.filter(owner=request.user).count(),
    })


@login_required
@require_http_methods(['GET', 'POST'])
def expense_edit(request, pk=None):
    expense = get_object_or_404(Expense, pk=pk, owner=request.user) if pk else None
    form = ExpenseForm(request.POST or None, instance=expense, user=request.user)
    if request.method == 'POST' and form.is_valid():
        saved = form.save()
        messages.success(request, 'Expense updated.' if expense else 'Expense added.')
        return redirect(f"/?month={saved.date:%Y-%m}")
    return render(request, 'tracking/expense_form.html', {'form': form, 'expense': expense})


@login_required
@require_http_methods(['GET', 'POST'])
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk, owner=request.user)
    if request.method == 'POST':
        month = expense.date.strftime('%Y-%m')
        expense.delete()
        messages.success(request, 'Expense deleted.')
        return redirect(f'/?month={month}')
    return render(request, 'tracking/expense_confirm_delete.html', {'expense': expense})


@login_required
@require_http_methods(['GET', 'POST'])
def categories(request):
    form = CategoryForm(request.POST or None, user=request.user)
    if request.method == 'POST' and form.is_valid():
        try:
            with transaction.atomic():
                form.save()
        except IntegrityError:
            form.add_error('name', 'You already have a category with this name.')
        else:
            messages.success(request, 'Category created. It is ready to use for your expenses.')
            return redirect('categories')
    return render(request, 'tracking/categories.html', {
        'form': form, 'categories': Category.objects.filter(owner=request.user),
    })


@login_required
@require_http_methods(['GET', 'POST'])
def budgets(request):
    month_form = BudgetMonthForm(request.GET if 'month' in request.GET else {
        'month': timezone.localdate().strftime('%Y-%m')})
    context = {'month_form': month_form}
    if not month_form.is_valid():
        return render(request, 'tracking/budgets.html', context, status=400)
    month = month_form.cleaned_data['month']
    categories = list(Category.objects.filter(owner=request.user))
    budget = MonthlyBudget.objects.filter(owner=request.user, month=month).first()
    source = budget or previous_budget(request.user, month)
    initial = {}
    if source:
        initial['overall'] = Decimal(source.amount_cents) / 100
        initial.update({f'category_{pk}': Decimal(cents) / 100
                        for pk, cents in source.limits.values_list('category_id', 'amount_cents')})
    form = BudgetForm(request.POST if request.method == 'POST' else None,
                      initial=initial, categories=categories)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            budget, _ = MonthlyBudget.objects.update_or_create(
                owner=request.user, month=month,
                defaults={'amount_cents': int(form.cleaned_data['overall'] * 100)})
            budget.limits.all().delete()
            CategoryLimit.objects.bulk_create([
                CategoryLimit(budget=budget, category=category,
                    amount_cents=int(form.cleaned_data[f'category_{category.pk}'] * 100))
                for category in categories if form.cleaned_data[f'category_{category.pk}'] is not None
            ])
        messages.success(request, f'Budget saved for {month:%B %Y}. Other months are unchanged.')
        return redirect(f'/budgets/?month={month:%Y-%m}')
    context.update({
        'form': form, 'month': month, 'budget': budget,
        'copy_source': source if not budget else None,
        **budget_summary(request.user, month, budget, categories),
    })
    return render(request, 'tracking/budgets.html', context)


@login_required
@require_http_methods(['GET'])
def dashboard(request):
    month_form = BudgetMonthForm(request.GET if 'month' in request.GET else {
        'month': timezone.localdate().strftime('%Y-%m')})
    if not month_form.is_valid():
        return render(request, 'tracking/dashboard.html', {'month_form': month_form}, status=400)
    month = month_form.cleaned_data['month']
    return render(request, 'tracking/dashboard.html', {
        'month_form': month_form, 'month': month, **dashboard_data(request.user, month),
    })
