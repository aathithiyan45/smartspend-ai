from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Add extra fields you want
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    full_name = models.CharField(max_length=150, blank=True, null=True)  # Add this
    last_name = models.CharField(max_length=150, blank=True, null=True)  # Add this

    def __str__(self):
        return f"{self.user.username}'s Profile"
