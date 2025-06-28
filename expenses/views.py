from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from datetime import datetime, date, timedelta
from django.http import HttpResponse
import json
import numpy as np
import csv
import calendar
from reportlab.pdfgen import canvas
from sklearn.linear_model import LinearRegression

from .models import Expense, CategoryBudget, SavingGoal
from .forms import ExpenseForm, CategoryBudgetForm, SavingGoalForm
from ml.model import predict_category


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

    current_total = Expense.objects.filter(
        user=request.user,
        date__month=this_month.month,
        date__year=this_month.year
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    previous_total = Expense.objects.filter(
        user=request.user,
        date__month=previous_month.month,
        date__year=previous_month.year
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    trend_percent = ((current_total - previous_total) / previous_total) * 100 if previous_total > 0 else 0
    trend_message = f"📊 This month's spending is {'up' if trend_percent > 0 else 'down'} by {abs(trend_percent):.1f}% compared to last month."

    budgets = CategoryBudget.objects.filter(user=request.user).order_by('-month')

    category_summary = []
    budget_feedback = []
    saving_tips = []

    for budget in budgets:
        spent = expenses.filter(category__iexact=budget.category).aggregate(total=Sum('amount'))['total'] or 0
        spent_float = float(spent)
        limit = float(budget.monthly_limit or 0)
        percent = round((spent_float / limit) * 100) if limit > 0 else 0

        if percent >= 100:
            status = "❌ Over Budget"
            budget_feedback.append(f"Overspent in '{budget.category}'. Consider increasing the budget limit.")
        elif percent >= 80:
            status = "⚠️ Almost Full"
        else:
            status = "✅ Under Budget"
            if percent < 50:
                budget_feedback.append(f"Used only {percent}% of '{budget.category}' budget. Maybe lower the budget next month.")

        # ✅ Added budget_id for edit/delete in templates
        category_summary.append({
            "category": budget.category,
            "limit": limit,
            "spent": spent_float,
            "percent": percent,
            "status": status,
            "budget_id": budget.id,
        })

        # 🔥 Saving Tips
        if spent_float > limit:
            excess = spent_float - limit
            saving_tips.append(
                f"🍽️ You overspent ₹{excess:.0f} in '{budget.category}'. Try reducing it by 20% to save ₹{(spent_float * 0.2):.0f}/month."
            )
        elif spent_float >= 0.8 * limit:
            saving_tips.append(
                f"⚠️ '{budget.category}' spending is almost full. Try cutting 10% to save ₹{(spent_float * 0.1):.0f}."
            )

    goals = SavingGoal.objects.filter(user=request.user)

    for goal in goals:
        saved = float(goal.current_amount or 0)
        target = float(goal.target_amount or 1)
        goal.progress_percent = round((saved / target) * 100)

        remaining = target - saved
        days_left = (goal.deadline - today).days
        if remaining > 0 and days_left > 0:
            per_day = remaining / days_left
            saving_tips.append(
                f"🏦 To reach '{goal.goal_name}', save ₹{per_day:.0f}/day for {days_left} more days."
            )

    context = {
        'expenses': expenses,
        'start': start_date,
        'end': end_date,
        'category_summary': category_summary,
        'goals': goals,
        'trend_message': trend_message,
        'budget_feedback': budget_feedback,
        'saving_tips': saving_tips,
        'budgets': budgets,
    }

    return render(request, 'home.html', context)



from .forms import ExpenseForm

@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            # ✅ category is already predicted inside the form.save() method
            expense.save()
            return redirect('home')
    else:
        form = ExpenseForm()
    return render(request, 'add_expense.html', {'form': form})

@login_required
def edit_expense(request, expense_id):
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
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    if request.method == 'POST':
        expense.delete()
        return redirect('home')
    return render(request, 'confirm_delete.html', {'expense': expense})

@login_required
def stats(request):
    total = Expense.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0
    categories = Expense.objects.filter(user=request.user).values('category').annotate(total=Sum('amount'))
    monthly = Expense.objects.filter(user=request.user).annotate(month=TruncMonth('date')).values('month').annotate(total=Sum('amount')).order_by('month')
    category_labels = [cat['category'] for cat in categories]
    category_totals = [float(cat['total']) for cat in categories]
    month_labels = [entry['month'].strftime('%b %Y') for entry in monthly]
    month_totals = [float(entry['total']) for entry in monthly]
    latest_month_label = month_labels[-1] if month_labels else None
    latest_month_total = month_totals[-1] if month_totals else 0
    top3_months = sorted([(entry['month'].strftime('%b %Y'), float(entry['total'])) for entry in monthly], key=lambda x: x[1], reverse=True)[:3]

    future_predictions = {}
    for cat in categories:
        category_name = cat['category']
        monthly_cat_data = Expense.objects.filter(user=request.user, category=category_name).annotate(month=TruncMonth('date')).values('month').annotate(total=Sum('amount')).order_by('month')
        if len(monthly_cat_data) >= 2:
            X = np.array([entry['month'].month for entry in monthly_cat_data]).reshape(-1, 1)
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
    budget_form = CategoryBudgetForm(request.POST or None)
    goal_form = SavingGoalForm(request.POST or None)

    if request.method == 'POST':
        if 'submit_budget' in request.POST and budget_form.is_valid():
            budget = budget_form.save(commit=False)
            budget.user = request.user
            month_str = request.POST.get('month')
            if month_str and len(month_str) == 7:
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

@login_required
def export_expenses_csv(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="expenses.csv"'
    writer = csv.writer(response)
    writer.writerow(['Date', 'Category', 'Amount', 'Title'])
    for expense in expenses:
        writer.writerow([expense.date, expense.category, expense.amount, expense.title])
    return response

@login_required
def export_expenses_pdf(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="expenses.pdf"'
    p = canvas.Canvas(response)
    p.setFont("Helvetica", 12)
    y = 800
    p.drawString(50, y, "Date       Category     Amount     Title")
    y -= 20
    for exp in expenses:
        p.drawString(50, y, f"{exp.date}   {exp.category}   ₹{exp.amount}   {exp.title}")
        y -= 20
        if y < 40:
            p.showPage()
            y = 800
    p.save()
    return response

@login_required
def edit_budget(request, budget_id):
    budget = get_object_or_404(CategoryBudget, id=budget_id, user=request.user)
    if request.method == 'POST':
        form = CategoryBudgetForm(request.POST, instance=budget)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = CategoryBudgetForm(instance=budget)
    return render(request, 'edit_budget.html', {'form': form})

@login_required
def delete_budget(request, budget_id):
    budget = get_object_or_404(CategoryBudget, id=budget_id, user=request.user)
    if request.method == 'POST':
        budget.delete()
        return redirect('home')
    return render(request, 'confirm_delete.html', {'object': budget, 'type': 'Budget'})

@login_required
def edit_goal(request, goal_id):
    goal = get_object_or_404(SavingGoal, id=goal_id, user=request.user)
    if request.method == 'POST':
        form = SavingGoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = SavingGoalForm(instance=goal)
    return render(request, 'edit_goal.html', {'form': form})

@login_required
def delete_goal(request, goal_id):
    goal = get_object_or_404(SavingGoal, id=goal_id, user=request.user)
    if request.method == 'POST':
        goal.delete()
        return redirect('home')
    return render(request, 'confirm_delete.html', {'object': goal, 'type': 'Saving Goal'})


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Expense
from utils.nlp_parser import extract_query_data
from django.db.models import Q
import datetime


@login_required
def smart_search(request):
    query = request.GET.get('query', '').strip()
    expenses = Expense.objects.filter(user=request.user)
    parsed = {}

    if query:
        try:
            parsed = extract_query_data(query)

            # 🎯 Filter by category (case-insensitive, partial match support)
            category = parsed.get('category')
            if category:
                expenses = expenses.filter(category__icontains=category)

            # 🗓️ Filter by date range
            start_date = parsed.get('start_date')
            end_date = parsed.get('end_date')

            if start_date and end_date:
                expenses = expenses.filter(date__range=(start_date, end_date))
            elif start_date:
                expenses = expenses.filter(date__gte=start_date)
            elif end_date:
                expenses = expenses.filter(date__lte=end_date)

            # 💬 Optional keyword search on title or description
            keywords = parsed.get('keywords')
            if keywords:
                for word in keywords.split():
                    expenses = expenses.filter(Q(title__icontains=word) | Q(description__icontains=word))

        except Exception as e:
            print("⚠️ NLP parse failed:", e)
            # Optional: You can show an error on UI via context['error'] = "..."

    # 📌 Always sort by most recent first
    expenses = expenses.order_by('-date')

    context = {
        'expenses': expenses,
        'query': query,
        'parsed': parsed,
        'results_count': expenses.count(),
    }

    return render(request, 'smart_search_results.html', context)

import re
import logging
from datetime import datetime, date
import pytesseract
from PIL import Image
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ReceiptUploadForm
from .models import ReceiptUpload, Expense

logger = logging.getLogger(__name__)

# 🔍 Predict category from text
def predict_category(text):
    text = text.lower()
    if any(word in text for word in ['petrol', 'fuel', 'diesel', 'shell']):
        return 'Travel'
    elif any(word in text for word in ['burger', 'restaurant', 'cafe', 'fries', 'dining']):
        return 'Food'
    elif any(word in text for word in ['milk', 'rice', 'supermarket', 'grocery', 'store']):
        return 'Groceries'
    elif any(word in text for word in ['book', 'course', 'tuition']):
        return 'Education'
    elif any(word in text for word in ['consultation', 'hospital', 'clinic', 'pharmacy']):
        return 'Healthcare'
    return 'Other'

# 🧾 Extract receipt info
def extract_receipt_info(text):
    text = text.replace('\r\n', '\n')

    # 💰 Amount extraction
    amount_match = re.findall(r'(?:[\₹\$]?\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', text)
    amounts = []
    for amt in amount_match:
        cleaned = amt.replace('₹', '').replace('$', '').replace(',', '').strip()
        try:
            amounts.append(float(cleaned))
        except:
            pass
    total_amount = max(amounts) if amounts else None

    # 📅 Date extraction
    date_match = re.findall(r'\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}', text)
    date_obj = None
    if date_match:
        raw_date = date_match[0].replace("\u201c", '').replace("\u201d", '')
        for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
            try:
                date_obj = datetime.strptime(raw_date, fmt).date()
                break
            except ValueError:
                continue

    # 🏷️ Title extraction
    lines = text.strip().split('\n')
    
    title = next((line.strip() for line in lines if line.strip() and not any(k in line.lower() for k in ['bill', 'date', 'invoice'])), None)
    if not title:
        title = "Untitled Receipt"
    

    # 🗂️ Category prediction
    category = predict_category(text)

    return {
        "title": title,
        "amount": total_amount,
        "date": date_obj,
        "category": category,
        "raw_text": text
    }


# 📤 Upload and process receipt
def upload_receipt(request):
    if request.method == 'POST':
        form = ReceiptUploadForm(request.POST, request.FILES)
        if form.is_valid():
            receipt = form.save(commit=False)
            receipt.user = request.user

            try:
                # 🧠 OCR extraction
                img = Image.open(receipt.image)
                text = pytesseract.image_to_string(img)
                logger.info("🔍 OCR Extracted Text:\n%s", text)

                # 📦 Extract receipt data
                extracted = extract_receipt_info(text)

                # ✅ Serialize date for JSONField
                if isinstance(extracted.get("date"), (datetime, date)):
                    extracted["date"] = extracted["date"].isoformat()

                receipt.extracted_data = extracted
                receipt.save()

                # ✅ Deserialize for Expense model
                if all([extracted.get("title"), extracted.get("amount"), extracted.get("date")]):
                    try:
                        date_obj = datetime.strptime(extracted["date"], "%Y-%m-%d").date()

                        Expense.objects.create(
                            user=request.user,
                            title=extracted["title"],
                            amount=extracted["amount"],
                            category=extracted["category"],
                            date=date_obj,
                            payment_method='cash',
                            notes='Imported via OCR'
                        )
                        logger.info("✅ Expense created from receipt.")
                    except Exception as date_err:
                        logger.error(f"❌ Failed to parse date: {date_err}")

                return redirect('receipt_detail', receipt_id=receipt.id)

            except Exception as e:
                logger.error(f"❌ Error processing receipt: {e}")
                form.add_error(None, "Failed to process receipt image. Please try another image.")
    else:
        form = ReceiptUploadForm()

    return render(request, 'upload_receipt.html', {'form': form})

# 📄 View receipt details
def receipt_detail(request, receipt_id):
    receipt = get_object_or_404(ReceiptUpload, id=receipt_id, user=request.user)
    return render(request, 'receipt_detail.html', {'receipt': receipt})
