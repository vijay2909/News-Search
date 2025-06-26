import requests
from django.conf import settings
from django.utils import timezone
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class NewsAPIClient:
    """
    Client class for interacting with News API.
    
    Attributes:
        api_key: API key for News API
        base_url: Base URL for News API endpoints
    """
    
    def __init__(self):
        self.api_key = settings.NEWS_API_KEY
        self.base_url = settings.NEWS_API_BASE_URL
    
    def search_everything(self, query, language='en', sort_by='publishedAt', 
                         page_size=100, from_date=None):
        """
        Search for news articles using News API everything endpoint.
        
        Args:
            query (str): Search query
            language (str): Language code for articles
            sort_by (str): Sort articles by (publishedAt, relevancy, popularity)
            page_size (int): Number of articles to retrieve
            from_date (datetime): Fetch articles published after this date
            
        Returns:
            dict: API response containing articles and metadata
        """
        url = f"{self.base_url}everything"
        
        params = {
            'q': query,
            'language': language,
            'sortBy': sort_by,
            'pageSize': page_size,
            'apiKey': self.api_key
        }
        
        if from_date:
            params['from'] = from_date.strftime('%Y-%m-%dT%H:%M:%S')
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"News API request failed: {e}")
            return {'status': 'error', 'message': str(e), 'articles': []}
    
    def get_sources(self, language='en', country=None, category=None):
        """
        Get available news sources from News API.
        
        Args:
            language (str): Language code
            country (str): Country code
            category (str): Category filter
            
        Returns:
            dict: API response containing sources
        """
        url = f"{self.base_url}sources"
        
        params = {
            'language': language,
            'apiKey': self.api_key
        }
        
        if country:
            params['country'] = country
        if category:
            params['category'] = category
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"News API sources request failed: {e}")
            return {'status': 'error', 'sources': []}


def parse_api_date(date_string):
    """
    Parse date string from News API to datetime object.
    
    Args:
        date_string (str): Date string from API
        
    Returns:
        datetime: Parsed datetime object
    """
    try:
        return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return timezone.now()


def get_trending_keywords(days=7, limit=10):
    """
    Get trending keywords based on search frequency.
    
    Args:
        days (int): Number of days to look back
        limit (int): Maximum number of keywords to return
        
    Returns:
        QuerySet: Trending keywords with search counts
    """
    from django.db.models import Count
    from .models import SearchLog
    
    start_date = timezone.now() - timezone.timedelta(days=days)
    
    return SearchLog.objects.filter(
        search_date__gte=start_date
    ).values(
        'keyword__keyword'
    ).annotate(
        search_count=Count('id'),
        unique_users=Count('user', distinct=True)
    ).order_by('-search_count')[:limit]

