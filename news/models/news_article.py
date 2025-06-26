from django.db import models
from django.contrib.auth.models import User
from news.models.keyword import Keyword

class NewsArticle(models.Model):
    """
    Model to store news articles fetched from the API.
    
    Attributes:
        keyword: ForeignKey to the keyword this article belongs to
        title: Article title
        description: Article description
        url: Original article URL
        image_url = models.URLField(max_length=500, null=True, blank=True)
        published_at: When article was published
        source_name: Name of the news source
        source_category: Category of the news source
        language: Article language
        content: Article content snippet
        created_at: When article was stored in database
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
        # Orders articles by publication date by default
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['published_at']),
            models.Index(fields=['source_name']),
            models.Index(fields=['language']),
        ]

    def __str__(self):
        return self.title[:100]
