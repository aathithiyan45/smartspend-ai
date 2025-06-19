from django.shortcuts import render, redirect, get_object_or_404
from .forms import ExpenseForm
from .models import Expense, CategoryBudget, SavingGoal
from ml.model import predict_category
from datetime import datetime, date
from django.db.models.functions import TruncMonth
from django.db.models import Sum
import json
from django.contrib.auth.decorators import login_required

# 🏠 Home Page with Date Filter and Budget Usage
@login_required
def home(request):
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')

    expenses = Expense.objects.all().order_by('-date')

    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
            expenses = expenses.filter(date__range=(start, end))
        except ValueError:
            pass  # Invalid date format

    # 🔁 Without auth, get all budgets set (or you can later hardcode user)
    today = date.today()
    budgets = CategoryBudget.objects.filter(month__month=today.month, month__year=today.year)

    summary = []
    for b in budgets:
        spent = expenses.filter(category__iexact=b.category).aggregate(total=Sum('amount'))['total'] or 0
        percent = round((spent / b.monthly_limit) * 100) if b.monthly_limit > 0 else 0
        status = "✅ Under Budget"
        if percent >= 100:
            status = "❌ Over Budget"
        elif percent >= 80:
            status = "⚠️ Almost Full"

        summary.append({
            "category": b.category,
            "limit": b.monthly_limit,
            "spent": spent,
            "percent": percent,
            "status": status
        })

    # 📌 No auth: show all goals (or later filter for one default user)
    goals = SavingGoal.objects.all()

    return render(request, 'home.html', {
        'expenses': expenses,
        'start': start_date,
        'end': end_date,
        'category_summary': summary,
        'goals': goals,
    })


# ➕ Add New Expense with AI
@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.category = predict_category(expense.title)
            expense.save()
            return redirect('home')
    else:
        form = ExpenseForm()

    return render(request, 'add_expense.html', {'form': form})


# ✏️ Edit Existing Expense
@login_required
def edit_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ExpenseForm(instance=expense)

    return render(request, 'edit_expense.html', {'form': form, 'expense': expense})


# ❌ Delete Confirmation
@login_required
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    if request.method == 'POST':
        expense.delete()
        return redirect('home')
    return render(request, 'confirm_delete.html', {'expense': expense})


# 📊 View Statistics
@login_required
def stats(request):
    total = Expense.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    categories = Expense.objects.values('category').annotate(total=Sum('amount'))

    monthly = (
        Expense.objects
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )

    category_labels = [cat['category'] for cat in categories]
    category_totals = [float(cat['total']) for cat in categories]

    month_labels = [entry['month'].strftime('%b %Y') for entry in monthly]
    month_totals = [float(entry['total']) for entry in monthly]

    return render(request, 'stats.html', {
        'total': total,
        'categories': categories,
        'category_labels': json.dumps(category_labels),
        'category_totals': json.dumps(category_totals),
        'month_labels': json.dumps(month_labels),
        'month_totals': json.dumps(month_totals),
        'trend_labels': json.dumps(month_labels),
        'trend_totals': json.dumps(month_totals),
    })
from .forms import CategoryBudgetForm, SavingGoalForm

@login_required
def budget_goals(request):
    budget_form = CategoryBudgetForm(request.POST or None)
    goal_form = SavingGoalForm(request.POST or None)

    if request.method == 'POST':
        if 'submit_budget' in request.POST and budget_form.is_valid():
            budget = budget_form.save(commit=False)  # Don't save yet
            budget.user = request.user              # Assign logged-in user
            budget.save()                           # Save now
            return redirect('budget_goals')

        if 'submit_goal' in request.POST and goal_form.is_valid():
            goal = goal_form.save(commit=False)
            goal.user = request.user                # Same for saving goal
            goal.save()
            return redirect('budget_goals')

    return render(request, 'budget_goals.html', {
        'budget_form': budget_form,
        'goal_form': goal_form,
    })
