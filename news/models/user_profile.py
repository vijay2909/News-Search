from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """
    Extended user profile model to manage user-specific configurations.
    
    Attributes:
        user: OneToOne relationship with Django User model
        keyword_quota: Maximum number of keywords user can track
        is_active: Whether user account is active
        created_at: Timestamp when profile was created
        updated_at: Timestamp when profile was last updated
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    keyword_quota = models.PositiveIntegerField(default=10)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - Profile"

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"