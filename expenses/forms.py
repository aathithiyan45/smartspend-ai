from django import forms
from django.utils import timezone
from datetime import date
import re
from .models import Expense
import joblib
import os
from django import forms
from datetime import date
import os
import joblib
from .models import Expense  # Ensure Expense model is imported

# ✅ Load ML model + vectorizer once
ML_MODEL_PATH = os.path.join('ml', 'category_model.pkl')
VEC_PATH = os.path.join('ml', 'vectorizer.pkl')

try:
    model = joblib.load(ML_MODEL_PATH)
    vectorizer = joblib.load(VEC_PATH)
except Exception as e:
    model = None
    vectorizer = None
    print(f"⚠️ Error loading ML model/vectorizer: {e}")


class ExpenseForm(forms.ModelForm):
    predicted_category = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )

    class Meta:
        model = Expense
        fields = ['title', 'amount', 'date', 'payment_method', 'notes']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-200 outline-none',
                'placeholder': 'What did you spend on? (e.g., Grocery shopping, Coffee, Gas)',
                'autocomplete': 'off'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-green-500 focus:ring-2 focus:ring-green-200 transition-all duration-200 outline-none',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-input w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all duration-200 outline-none'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-orange-500 focus:ring-2 focus:ring-orange-200 transition-all duration-200 outline-none bg-white'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-textarea w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all duration-200 outline-none resize-none',
                'rows': 3,
                'placeholder': 'Any additional notes or details... (optional)'
            }),
        }

    def __init__(self, *args, **kwargs):
        super(ExpenseForm, self).__init__(*args, **kwargs)
        self.fields['date'].initial = date.today()

        # Optional: tag each field for JS or analytics
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'data-field': field_name})

    def predict_category(self, title):
        if not model or not vectorizer or not title:
            return "Other"
        try:
            X = vectorizer.transform([title.lower()])
            return model.predict(X)[0]
        except Exception as e:
            print(f"Prediction error: {e}")
            return "Other"

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title:
            self.cleaned_data['predicted_category'] = self.predict_category(title)
        return title

    def save(self, commit=True):
        instance = super().save(commit=False)
        if hasattr(self, 'cleaned_data') and 'predicted_category' in self.cleaned_data:
            instance.category = self.cleaned_data['predicted_category']
        elif self.cleaned_data.get('title'):
            instance.category = self.predict_category(self.cleaned_data['title'])

        if commit:
            instance.save()
        return instance


from django import forms
from .models import CategoryBudget, SavingGoal
from datetime import date

class CategoryBudgetForm(forms.ModelForm):
    class Meta:
        model = CategoryBudget
        fields = ['category', 'monthly_limit', 'month']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'monthly_limit': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Set monthly limit'}),
            'month': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['month'].initial = date.today().replace(day=1)

class SavingGoalForm(forms.ModelForm):
    class Meta:
        model = SavingGoal
        fields = ['goal_name', 'target_amount', 'current_amount', 'deadline']
        widgets = {
            'goal_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Goal name'}),
            'target_amount': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Target amount'}),
            'current_amount': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Current amount (optional)'}),
            'deadline': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['deadline'].initial = date.today()

# forms.py
from django import forms
from .models import ReceiptUpload

class ReceiptUploadForm(forms.ModelForm):
    class Meta:
        model = ReceiptUpload
        fields = ['image']