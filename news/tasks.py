from background_task import background
from .models import Keyword, NewsArticle
import requests
from django.conf import settings
from django.utils import timezone
from dateutil import parser
from datetime import timedelta
import os

# The master task will run every 5 minutes (300 seconds) to check for jobs
MASTER_TASK_INTERVAL = 300
# The global default refresh interval (if no custom one is set)
# Fetches from .env, defaults to 1 hour (3600s)
REFRESH_INTERVAL_GLOBAL = int(os.getenv('BACKGROUND_TASK_REFRESH_INTERVAL', 3600))


@background(schedule=10, repeat=MASTER_TASK_INTERVAL)
def refresh_all_keywords_master():
    """
    The main repeating background task. It runs frequently, checks all keywords,
    and decides if they need a refresh based on their individual interval.
    """
    print(f"MASTER TASK: Checking all keywords for scheduled refresh...")
    keywords = Keyword.objects.all()
    for keyword in keywords:
        interval = keyword.custom_refresh_interval or REFRESH_INTERVAL_GLOBAL

        # If the keyword has never been searched, or if enough time has passed, run the fetch
        if keyword.last_searched is None or (timezone.now() - keyword.last_searched > timedelta(seconds=interval)):
            _fetch_for_keyword(keyword.id)


def _fetch_for_keyword(keyword_id):
    """A helper function to fetch articles for a single keyword."""
    print(f"HELPER: Fetching articles for keyword_id: {keyword_id}")
    try:
        keyword = Keyword.objects.get(id=keyword_id)
    except Keyword.DoesNotExist:
        return

    api_key = settings.NEWS_API_KEY
    if not api_key: return

    latest_article = keyword.articles.order_by('-published_at').first()
    url = f'https://newsapi.org/v2/everything?q="{keyword.keyword}"&apiKey={api_key}&sortBy=publishedAt'

    if latest_article:
        from_date = (latest_article.published_at + timedelta(seconds=1)).isoformat()
        url += f'&from={from_date}'

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException:
        return

    for article_data in data.get('articles', []):
        if not NewsArticle.objects.filter(url=article_data['url']).exists():
            try:
                if not article_data.get('publishedAt'): continue
                NewsArticle.objects.create(
                    keyword=keyword,
                    title=article_data.get('title'),
                    description=article_data.get('description') or '',
                    content=article_data.get('content') or '',
                    url=article_data.get('url'),
                    url_to_image=article_data.get('urlToImage'),
                    published_at=parser.isoparse(article_data['publishedAt']),
                    source_name=article_data.get('source', {}).get('name', 'Unknown Source'),
                    language=article_data.get('language', 'en')
                )
            except Exception as e:
                print(f"ERROR saving article: {e}")

    keyword.last_searched = timezone.now()
    keyword.save()
