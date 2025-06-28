from django.db import models
from news.models.keyword import Keyword

class NewsArticle(models.Model):
    """
    Represents a single news article fetched from the News API.

    Each article is associated with a keyword and stores all relevant
    information needed for display and filtering.

    Attributes:
        keyword (ForeignKey): The Keyword that this article was found under.
        title (CharField): The headline or title of the article.
        description (TextField): A short summary or description of the article.
        url (URLField): The direct URL to the full, original article.
        url_to_image (URLField): A URL for a relevant image provided by the API.
        published_at (DateTimeField): The exact date and time the article was published.
        source_name (CharField): The name of the news source (e.g., "BBC News").
        source_category (CharField): The category of the news source, if available.
        language (CharField): The language of the article (e.g., "en", "es").
        content (TextField): A snippet of the article's content, if available.
        created_at (DateTimeField): The timestamp when the article was saved to our database.
    """
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE, related_name='articles')
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    url = models.URLField(unique=True)
    url_to_image = models.URLField(blank=True, null=True)
    published_at = models.DateTimeField()
    source_name = models.CharField(max_length=200)
    source_category = models.CharField(max_length=100, blank=True)
    language = models.CharField(max_length=10, default='en')
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Default ordering for queries is the newest articles first.
        ordering = ['-published_at']
        # Database indexes to speed up common filtering operations.
        indexes = [
            models.Index(fields=['published_at']),
            models.Index(fields=['source_name']),
            models.Index(fields=['language']),
        ]

    def __str__(self):
        """Returns a string representation of the article, which is its title."""
        return self.title[:100]
