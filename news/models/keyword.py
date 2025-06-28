from django.db import models
from django.contrib.auth.models import User

class Keyword(models.Model):
    """
    Represents a search keyword tracked by a user.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    keyword = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    last_searched = models.DateTimeField(null=True, blank=True)
    # ADDED THIS FIELD:
    custom_refresh_interval = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Custom refresh interval in seconds. Leave blank to use the global default."
    )

    class Meta:
        unique_together = ('user', 'keyword')

    def __str__(self):
        return self.keyword
