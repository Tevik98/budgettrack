from decimal import Decimal

from django import forms
from django.utils import timezone

from .models import Category, Expense


class ExpenseForm(forms.ModelForm):
    amount = forms.DecimalField(
        label='Amount (USD)', min_value=Decimal('0.01'), max_digits=10,
        decimal_places=2, widget=forms.NumberInput(attrs={
            'step': '0.01', 'min': '0.01', 'placeholder': '0.00', 'inputmode': 'decimal',
        }),
    )

    class Meta:
        model = Expense
        fields = ['amount', 'date', 'category', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'description': forms.TextInput(attrs={'placeholder': 'What was it for? (optional)'}),
        }

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.owner = user
        self.fields['category'].queryset = Category.objects.filter(owner=user)
        if self.instance.pk:
            self.fields['amount'].initial = self.instance.amount
        else:
            self.fields['date'].initial = timezone.localdate()

    def save(self, commit=True):
        self.instance.amount_cents = int(self.cleaned_data['amount'] * 100)
        return super().save(commit=commit)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        labels = {'name': 'Category name'}
        widgets = {'name': forms.TextInput(attrs={'placeholder': 'e.g. Pets or Education'})}

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.owner = user

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        if Category.objects.filter(owner=self.instance.owner, name__iexact=name).exists():
            raise forms.ValidationError('You already have a category with this name.')
        return name


class ExpenseFilterForm(forms.Form):
    month = forms.DateField(
        required=False, input_formats=['%Y-%m'],
        widget=forms.DateInput(attrs={'type': 'month'}, format='%Y-%m'),
    )
    category = forms.ModelChoiceField(queryset=Category.objects.none(), required=False,
                                     empty_label='All categories')

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(owner=user)


class BudgetMonthForm(forms.Form):
    month = forms.DateField(input_formats=['%Y-%m'],
        widget=forms.DateInput(attrs={'type': 'month'}, format='%Y-%m'))


class BudgetForm(forms.Form):
    overall = forms.DecimalField(label='Monthly budget (USD)', min_value=Decimal('0'),
        max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'inputmode': 'decimal'}))

    def __init__(self, *args, categories, **kwargs):
        super().__init__(*args, **kwargs)
        for category in categories:
            self.fields[f'category_{category.pk}'] = forms.DecimalField(
                label=category.name, required=False, min_value=Decimal('0'),
                max_digits=10, decimal_places=2,
                widget=forms.NumberInput(attrs={'step': '0.01', 'min': '0',
                    'placeholder': 'No limit', 'inputmode': 'decimal'}))
