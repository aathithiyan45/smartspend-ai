from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add/', views.add_expense, name='add_expense'),
    path('edit/<int:expense_id>/', views.edit_expense, name='edit_expense'),
    path('delete/<int:expense_id>/', views.delete_expense, name='delete_expense'),
    path('stats/', views.stats, name='stats'),  # 👈 New stats route
    path('budget-goals/', views.budget_goals, name='budget_goals'),
    path('export/csv/', views.export_expenses_csv, name='export_csv'),
    path('export/pdf/', views.export_expenses_pdf, name='export_pdf'),
    
    
]
