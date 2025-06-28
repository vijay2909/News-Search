"""
Data models for the 'news' application.

This file defines the database structure for storing keywords tracked by users
and the news articles associated with those keywords.
"""
from django.db import models
from django.contrib.auth.models import User

class Keyword(models.Model):
    """
    Represents a search keyword tracked by a specific user.

    This model links a user to a piece of text they want to search for,
    and stores metadata about when it was last searched and any custom
    refresh intervals set by an admin.

    Attributes:
        user (ForeignKey): A reference to the User who owns this keyword.
        keyword (CharField): The actual text of the keyword (e.g., "tesla").
        created_at (DateTimeField): The timestamp when the keyword was first added.
        last_searched (DateTimeField): The timestamp of the most recent API search
            for this keyword. Null if never searched.
        custom_refresh_interval (PositiveIntegerField): A custom interval in seconds
            for the background task to refresh this keyword. If null, the global
            default interval is used.
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
        """Returns a string representation of the keyword, which is its text."""
        return self.keyword
