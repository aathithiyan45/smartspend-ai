from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from datetime import datetime, date, timedelta
import json
import calendar

from .models import Expense, CategoryBudget, SavingGoal
from .forms import ExpenseForm, CategoryBudgetForm, SavingGoalForm
from ml.model import predict_category
from sklearn.linear_model import LinearRegression
import numpy as np



@login_required
def home(request):
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')

    expenses = Expense.objects.filter(user=request.user).order_by('-date')

    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
            expenses = expenses.filter(date__range=(start, end))
        except ValueError:
            pass

    today = date.today()
    this_month = today.replace(day=1)
    previous_month = (this_month - timedelta(days=1)).replace(day=1)

    # Calculate current and previous month totals
    current_total = Expense.objects.filter(user=request.user, date__month=this_month.month, date__year=this_month.year).aggregate(Sum('amount'))['amount__sum'] or 0
    previous_total = Expense.objects.filter(user=request.user, date__month=previous_month.month, date__year=previous_month.year).aggregate(Sum('amount'))['amount__sum'] or 0

    # Trend percentage
    if previous_total > 0:
        trend_percent = ((current_total - previous_total) / previous_total) * 100
    else:
        trend_percent = 0  # Avoid division by zero

    trend_message = f"📊 This month's spending is {'up' if trend_percent > 0 else 'down'} by {abs(trend_percent):.1f}% compared to last month."

    # Budgets
    budgets = CategoryBudget.objects.filter(user=request.user, month__month=today.month, month__year=today.year)

    category_summary = []
    budget_feedback = []

    for budget in budgets:
        spent = expenses.filter(category__iexact=budget.category).aggregate(total=Sum('amount'))['total'] or 0
        percent = round((spent / budget.monthly_limit) * 100) if budget.monthly_limit > 0 else 0

        if percent >= 100:
            status = "❌ Over Budget"
            budget_feedback.append(f"Overspent in '{budget.category}'. Consider increasing the budget limit.")
        elif percent >= 80:
            status = "⚠️ Almost Full"
        else:
            status = "✅ Under Budget"
            if percent < 50:
                budget_feedback.append(f"Used only {percent}% of '{budget.category}' budget. Maybe lower the budget next month.")

        category_summary.append({
            "category": budget.category,
            "limit": budget.monthly_limit,
            "spent": spent,
            "percent": percent,
            "status": status
        })

    goals = SavingGoal.objects.filter(user=request.user)

    context = {
        'expenses': expenses,
        'start': start_date,
        'end': end_date,
        'category_summary': category_summary,
        'goals': goals,
        'trend_message': trend_message,
        'budget_feedback': budget_feedback,
    }

    return render(request, 'home.html', context)


@login_required
def add_expense(request):
    """Add a new expense, auto-predicting category."""
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.category = predict_category(expense.title)
            expense.save()
            return redirect('home')
    else:
        form = ExpenseForm()
    return render(request, 'add_expense.html', {'form': form})


@login_required
def edit_expense(request, expense_id):
    """Edit an existing expense by ID."""
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'edit_expense.html', {'form': form, 'expense': expense})


@login_required
def delete_expense(request, expense_id):
    """Delete an expense after confirmation."""
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    if request.method == 'POST':
        expense.delete()
        return redirect('home')
    return render(request, 'confirm_delete.html', {'expense': expense})

@login_required
def stats(request):
    """Show aggregate stats: total, category-wise, monthly trends, and future predictions."""
    total = Expense.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0

    categories = (
        Expense.objects.filter(user=request.user)
        .values('category')
        .annotate(total=Sum('amount'))
    )

    monthly = (
        Expense.objects.filter(user=request.user)
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )

    category_labels = [cat['category'] for cat in categories]
    category_totals = [float(cat['total']) for cat in categories]

    month_labels = [entry['month'].strftime('%b %Y') for entry in monthly]
    month_totals = [float(entry['total']) for entry in monthly]

    latest_month_label = month_labels[-1] if month_labels else None
    latest_month_total = month_totals[-1] if month_totals else 0

    # Top 3 months
    top3_qs = sorted(monthly, key=lambda x: x['total'], reverse=True)[:3]
    top3_months = [
        (entry['month'].strftime('%b %Y'), float(entry['total']))
        for entry in top3_qs
    ]

    # 📅 Future Expense Prediction per Category
    future_predictions = {}
    for cat in categories:
        category_name = cat['category']
        monthly_cat_data = (
            Expense.objects.filter(user=request.user, category=category_name)
            .annotate(month=TruncMonth('date'))
            .values('month')
            .annotate(total=Sum('amount'))
            .order_by('month')
        )

        if len(monthly_cat_data) >= 2:
            X = np.array(range(len(monthly_cat_data))).reshape(-1, 1)
            y = np.array([float(entry['total']) for entry in monthly_cat_data])
            model = LinearRegression()
            model.fit(X, y)

            next_month_index = np.array([[len(monthly_cat_data)]])
            predicted = model.predict(next_month_index)[0]
            future_predictions[category_name] = round(predicted, 2)

    context = {
        'total': total,
        'categories': categories,
        'category_labels': json.dumps(category_labels),
        'category_totals': json.dumps(category_totals),
        'month_labels': json.dumps(month_labels),
        'month_totals': json.dumps(month_totals),
        'trend_labels': json.dumps(month_labels),
        'trend_totals': json.dumps(month_totals),

        'latest_month_label': latest_month_label,
        'latest_month_total': latest_month_total,
        'top3_months': top3_months,
        'future_predictions': json.dumps(future_predictions),
    }

    return render(request, 'stats.html', context)


@login_required
def budget_goals(request):
    """View to add new budgets and saving goals, and show current ones."""
    budget_form = CategoryBudgetForm(request.POST or None)
    goal_form = SavingGoalForm(request.POST or None)

    if request.method == 'POST':
        if 'submit_budget' in request.POST and budget_form.is_valid():
            budget = budget_form.save(commit=False)
            budget.user = request.user

            month_str = request.POST.get('month')
            if month_str and len(month_str) == 7:  # Expecting YYYY-MM
                budget.month = datetime.strptime(month_str, '%Y-%m').date().replace(day=1)
            else:
                budget.month = date.today().replace(day=1)

            budget.save()
            return redirect('budget_goals')

        if 'submit_goal' in request.POST and goal_form.is_valid():
            goal = goal_form.save(commit=False)
            goal.user = request.user
            goal.save()
            return redirect('budget_goals')

    budgets = CategoryBudget.objects.filter(user=request.user).order_by('-month')
    goals = SavingGoal.objects.filter(user=request.user).order_by('deadline')

    context = {
        'budget_form': budget_form,
        'goal_form': goal_form,
        'budgets': budgets,
        'goals': goals,
    }
    return render(request, 'budget_goals.html', context)
