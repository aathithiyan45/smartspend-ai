from django.contrib import admin
from .models import CategoryBudget, SavingGoal, Expense

@admin.register(CategoryBudget)
class CategoryBudgetAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'monthly_limit', 'month')
    list_filter = ('category', 'month')
    search_fields = ('user__username', 'category')

@admin.register(SavingGoal)
class SavingGoalAdmin(admin.ModelAdmin):
    list_display = ('user', 'goal_name', 'target_amount', 'deadline')
    search_fields = ('user__username', 'goal_name')

# If you have an Expense model:
# admin.site.register(Expense)
