from django.db import models
from django.contrib.auth.models import User

from news.models.keyword import Keyword

class SearchLog(models.Model):
    """
    Model to log search activities for analytics and trending keywords.
    
    Attributes:
        keyword: ForeignKey to keyword that was searched
        user: ForeignKey to user who performed search
        search_date: When search was performed
        results_count: Number of results returned
        api_call_made: Whether actual API call was made or cached results used
    """
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    search_date = models.DateTimeField(auto_now_add=True)
    results_count = models.PositiveIntegerField(default=0)
    api_call_made = models.BooleanField(default=True)

    class Meta:
        ordering = ['-search_date']

    def __str__(self):
        return f"{self.user.username} searched '{self.keyword.keyword}' on {self.search_date}"
