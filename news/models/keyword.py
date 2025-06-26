from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Keyword(models.Model):
    """
    Model to store search keywords for each user.
    
    Attributes:
        user: ForeignKey to User who created the keyword
        keyword: The search term
        created_at: When keyword was first searched
        last_searched: Last time this keyword was searched
        search_count: Total number of searches for this keyword
        is_active: Whether keyword is actively being tracked
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='keywords')
    keyword = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    last_searched = models.DateTimeField(auto_now=True)
    search_count = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['user', 'keyword']
        ordering = ['-last_searched']

    def __str__(self):
        return f"{self.user.username} - {self.keyword}"

    def can_search_now(self):
        """
        Check if enough time has passed since last search based on cooldown period.
        
        Returns:
            bool: True if search is allowed, False otherwise
        """
        cooldown_period = timezone.now() - timedelta(minutes=15)
        return self.last_searched <= cooldown_period
