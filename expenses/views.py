from django.shortcuts import render, redirect, get_object_or_404
from .forms import ExpenseForm
from .models import Expense

# ✅ Import AI model
from ml.model import predict_category

# 🏠 Home view to list all expenses
from datetime import datetime
from django.shortcuts import render
from .models import Expense

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
            pass  # Invalid date input; ignore filtering

    return render(request, 'home.html', {
        'expenses': expenses,
        'start': start_date,
        'end': end_date,
    })

# ➕ Add new expense with AI-based category prediction
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)

            # 🔮 Predict category using title
            predicted_category = predict_category(expense.title)
            expense.category = predicted_category

            expense.save()
            return redirect('home')
    else:
        form = ExpenseForm()
    return render(request, 'add_expense.html', {'form': form})

# ✏️ Edit an existing expense manually
def edit_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'edit_expense.html', {'form': form})

# ❌ Delete confirmation page and deletion
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    if request.method == 'POST':
        expense.delete()
        return redirect('home')
    return render(request, 'confirm_delete.html', {'expense': expense})
import json
from django.db.models.functions import TruncMonth
from django.db.models import Sum
from .models import Expense
from django.shortcuts import render

def stats(request):
    # Total spent
    total = Expense.objects.aggregate(Sum('amount'))['amount__sum'] or 0

    # Category-wise totals
    categories = Expense.objects.values('category').annotate(total=Sum('amount'))

    # Monthly totals
    monthly = (
        Expense.objects
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )

    # For category pie chart
    category_labels = [cat['category'] for cat in categories]
    category_totals = [float(cat['total']) for cat in categories]

    # For monthly and trend charts
    month_labels = [entry['month'].strftime('%b %Y') for entry in monthly]
    month_totals = [float(entry['total']) for entry in monthly]

    # Trend chart data (same as monthly)
    trend_labels = month_labels
    trend_totals = month_totals

    return render(request, 'stats.html', {
        'total': total,
        'categories': categories,
        'monthly': monthly,
        'category_labels': json.dumps(category_labels),
        'category_totals': json.dumps(category_totals),
        'month_labels': json.dumps(month_labels),
        'month_totals': json.dumps(month_totals),
        'trend_labels': json.dumps(trend_labels),
        'trend_totals': json.dumps(trend_totals),
    })
