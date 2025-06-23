from django.db import models
from django.conf import settings
from django.utils import timezone


class Expense(models.Model):
    PAYMENT_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('upi', 'UPI'),
        ('netbanking', 'Net Banking'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100, blank=True, null=True)  # AI-predicted category
    date = models.DateField()
    payment_method = models.CharField(max_length=50, choices=PAYMENT_CHOICES, default='cash')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - ₹{self.amount}"


class CategoryBudget(models.Model):
    CATEGORY_CHOICES = [
        ('food', 'Food'),
        ('transport', 'Transportation'),
        ('entertainment', 'Entertainment'),
        ('shopping', 'Shopping'),
        ('healthcare', 'Healthcare'),
        ('utilities', 'Utilities'),
        ('education', 'Education'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    monthly_limit = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.DateField(help_text="Use the 1st of the month to represent that month")

    def __str__(self):
        return f"{self.user.username} - {self.category} - ₹{self.monthly_limit}"


class SavingGoal(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    goal_name = models.CharField(max_length=100)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)
    deadline = models.DateField()

    def __str__(self):
        return f"{self.goal_name} - ₹{self.target_amount} by {self.deadline}"


class ReceiptUpload(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='receipts/')
    uploaded_at = models.DateTimeField(default=timezone.now)
    extracted_data = models.JSONField(blank=True, null=True)  # Stores title, amount, date, category, raw_text

    def __str__(self):
        return f"Receipt #{self.id} by {self.user.username}"
