from django.urls import path
from . import views

urlpatterns = [
    # 🌐 Home & Dashboard
    path('', views.home, name='home'),

    # 💸 Expense Operations
    path('add/', views.add_expense, name='add_expense'),
    path('edit/<int:expense_id>/', views.edit_expense, name='edit_expense'),
    path('delete/<int:expense_id>/', views.delete_expense, name='delete_expense'),

    # 📊 Stats Page
    path('stats/', views.stats, name='stats'),

    # 📅 Budget & Saving Goals Page
    path('budget-goals/', views.budget_goals, name='budget_goals'),

    # 📤 Export Features
    path('export/csv/', views.export_expenses_csv, name='export_csv'),
    path('export/pdf/', views.export_expenses_pdf, name='export_pdf'),

    # 🧠 Budget CRUD
    path('budget/edit/<int:budget_id>/', views.edit_budget, name='edit_budget'),
    path('budget/delete/<int:budget_id>/', views.delete_budget, name='delete_budget'),

    # 🎯 Saving Goal CRUD
    path('goal/edit/<int:goal_id>/', views.edit_goal, name='edit_goal'),
    path('goal/delete/<int:goal_id>/', views.delete_goal, name='delete_goal'),
    
    path('smart-search/', views.smart_search, name='smart_search'),
    
    path('upload-receipt/', views.upload_receipt, name='upload_receipt'),
    path('receipt/<int:receipt_id>/', views.receipt_detail, name='receipt_detail'),

]
