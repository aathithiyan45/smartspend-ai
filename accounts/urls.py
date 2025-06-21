from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),        # User registration page
    path('login/', views.user_login, name='login'),             # User login page
    path('logout/', views.user_logout, name='logout'),          # Logout view
    path('profile/', views.profile_view, name='profile'),       # Profile display page (view only)
    path('profile/edit/', views.edit_profile, name='edit_profile'),  # Profile edit page (form)
]
