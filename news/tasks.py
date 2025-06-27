from background_task import background
from .models import Keyword, NewsArticle
import requests
from django.conf import settings
from django.utils import timezone
from dateutil import parser
from datetime import timedelta


@background(schedule=10)
def refresh_all_keywords():
    """
    This is the main repeating background task. It finds all keywords
    in the database and calls the helper function to refresh each one.
    This task should be scheduled to run only ONCE.
    """
    keywords = Keyword.objects.all()
    print(f"MAIN REFRESH TASK: Found {keywords.count()} keywords to process.")
    for keyword in keywords:
        # Call the helper function for each keyword
        _fetch_for_keyword(keyword.id)


def _fetch_for_keyword(keyword_id):
    """
    A helper function that contains the logic to fetch articles for a single keyword.
    This is no longer a background task itself but is called by the main repeating task.
    """
    print(f"BACKGROUND_TASK: Running for keyword_id: {keyword_id}")
    try:
        keyword = Keyword.objects.get(id=keyword_id)
    except Keyword.DoesNotExist:
        print(f"BACKGROUND_TASK: Keyword with id {keyword_id} not found. Aborting.")
        return

    api_key = settings.NEWS_API_KEY
    if not api_key:
        print("BACKGROUND_TASK_ERROR: News API key is not configured.")
        return

    latest_article = keyword.articles.order_by('-published_at').first()

    url = (f'https://newsapi.org/v2/everything?'
           f'q="{keyword.keyword}"&'
           f'apiKey={api_key}&'
           f'sortBy=publishedAt')

    if latest_article:
        from_date = (latest_article.published_at + timedelta(seconds=1)).isoformat()
        url += f'&from={from_date}'

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"BACKGROUND_TASK_ERROR: API request failed for '{keyword.keyword}': {e}")
        return

    new_articles_found = 0
    for article_data in data.get('articles', []):
        if not NewsArticle.objects.filter(url=article_data['url']).exists():
            try:
                if not article_data.get('publishedAt'):
                    continue

                published_time = parser.isoparse(article_data['publishedAt'])

                NewsArticle.objects.create(
                    keyword=keyword,
                    title=article_data.get('title'),
                    description=article_data.get('description') or '',
                    content=article_data.get('content') or '',
                    url=article_data.get('url'),
                    url_to_image=article_data.get('urlToImage'),
                    published_at=published_time,
                    source_name=article_data.get('source', {}).get('name', 'Unknown Source'),
                    language=article_data.get('language', 'en')
                )
                new_articles_found += 1
            except Exception as e:
                print(f"BACKGROUND_TASK_ERROR: Could not save article '{article_data.get('title')}': {e}")

    keyword.last_searched = timezone.now()
    keyword.save()

    if new_articles_found > 0:
        print(f"BACKGROUND_TASK: Found {new_articles_found} new articles for '{keyword.keyword}'.")
    else:
        print(f"BACKGROUND_TASK: No new articles found for '{keyword.keyword}'.")
