from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

# User Registration Form (extends Django's UserCreationForm)
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)  # Make email required

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

# Profile Form for editing bio, avatar, and user's first/last name
class ProfileForm(forms.ModelForm):
    # Adding user first_name and last_name fields manually since they're on User model
    first_name = forms.CharField(max_length=30, required=False, label='First Name')
    last_name = forms.CharField(max_length=30, required=False, label='Last Name')

    class Meta:
        model = Profile
        fields = ['bio', 'avatar']

    def __init__(self, *args, **kwargs):
        # Expecting a 'user' instance passed explicitly when form is created
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            # Initialize first_name and last_name from user object
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name

    def save(self, commit=True):
        # Save profile data
        profile = super().save(commit=False)
        user = profile.user

        # Update User's first and last names from form cleaned data
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')

        if commit:
            user.save()      # Save User first
            profile.save()   # Save Profile next

        return profile  # Return the profile instance
