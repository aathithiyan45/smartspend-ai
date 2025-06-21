from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegisterForm

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        print('POST data:', request.POST)
        if form.is_valid():
            print('Form is valid')
            user = form.save()
            messages.success(request, 'Your account has been created. You can now log in.')
            return redirect('login')
        else:
            print('Form errors:', form.errors)
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome {username}!')
                return redirect('home')  # change to your home page url name
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

from django.contrib.auth.decorators import login_required

@login_required
def user_logout(request):
    logout(request)
    messages.info(request, 'Logged out successfully.')
    return redirect('login')
# accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm

@login_required
def profile_view(request):
    profile = request.user.profile
    return render(request, 'accounts/profile.html', {'profile': profile})
@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # or the name of your profile view url
    else:
        form = ProfileForm(instance=profile, user=request.user)

    return render(request, 'accounts/edit_profile.html', {'form': form})

