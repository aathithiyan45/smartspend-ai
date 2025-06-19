from django import forms
from .models import Expense, CategoryBudget, SavingGoal
from datetime import date


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['title', 'amount', 'category', 'date', 'payment_method', 'notes']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input w-full p-2 border border-gray-300 rounded', 'placeholder': 'Enter title'}),
            'amount': forms.NumberInput(attrs={'class': 'form-input w-full p-2 border border-gray-300 rounded', 'placeholder': 'Enter amount'}),
            'category': forms.TextInput(attrs={'class': 'form-input w-full p-2 border border-gray-300 rounded', 'placeholder': 'Category (e.g. Food)'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input w-full p-2 border border-gray-300 rounded'}),
            'payment_method': forms.Select(attrs={'class': 'form-select w-full p-2 border border-gray-300 rounded'}),
            'notes': forms.Textarea(attrs={'class': 'form-textarea w-full p-2 border border-gray-300 rounded', 'rows': 3, 'placeholder': 'Optional notes...'}),
        }

    def __init__(self, *args, **kwargs):
        super(ExpenseForm, self).__init__(*args, **kwargs)
        self.fields['date'].initial = date.today()


class CategoryBudgetForm(forms.ModelForm):
    class Meta:
        model = CategoryBudget
        fields = ['category', 'monthly_limit', 'month']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select w-full p-2 border border-gray-300 rounded'}),
            'monthly_limit': forms.NumberInput(attrs={'class': 'form-input w-full p-2 border border-gray-300 rounded', 'placeholder': 'Set monthly limit'}),
            'month': forms.DateInput(attrs={'type': 'date', 'class': 'form-input w-full p-2 border border-gray-300 rounded'}),
        }

    def __init__(self, *args, **kwargs):
        super(CategoryBudgetForm, self).__init__(*args, **kwargs)
        self.fields['month'].initial = date.today().replace(day=1)


class SavingGoalForm(forms.ModelForm):
    class Meta:
        model = SavingGoal
        fields = ['goal_name', 'target_amount', 'deadline']
        widgets = {
            'goal_name': forms.TextInput(attrs={'class': 'form-input w-full p-2 border border-gray-300 rounded', 'placeholder': 'e.g. Buy Laptop'}),
            'target_amount': forms.NumberInput(attrs={'class': 'form-input w-full p-2 border border-gray-300 rounded', 'placeholder': 'Target ₹ amount'}),
            'deadline': forms.DateInput(attrs={'type': 'date', 'class': 'form-input w-full p-2 border border-gray-300 rounded'}),
        }

    def __init__(self, *args, **kwargs):
        super(SavingGoalForm, self).__init__(*args, **kwargs)
        self.fields['deadline'].initial = date.today()
