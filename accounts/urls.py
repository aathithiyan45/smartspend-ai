from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import profile_view

urlpatterns = [
    # ✅ Custom Register View
    path('register/', views.register, name='register'),

    # ✅ Built-in Login View with custom template
    path('login/', auth_views.LoginView.as_view(
        template_name='accounts/login.html',
        redirect_authenticated_user=True
    ), name='login'),

    # ✅ Secure Logout View with redirection
    path('logout/', auth_views.LogoutView.as_view(
        next_page='login'  # redirects after logout
    ), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
     
]
