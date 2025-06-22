from django.contrib import admin
from .models import Expense, CategoryBudget, SavingGoal

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'amount', 'category', 'date', 'user')
    list_filter = ('category', 'date')
    search_fields = ('title', 'category')

@admin.register(CategoryBudget)
class CategoryBudgetAdmin(admin.ModelAdmin):
    list_display = ('category', 'monthly_limit', 'month', 'user')
    list_filter = ('month',)

@admin.register(SavingGoal)
class SavingGoalAdmin(admin.ModelAdmin):
    list_display = ('goal_name', 'target_amount', 'deadline', 'user')  # Removed 'saved_amount'
