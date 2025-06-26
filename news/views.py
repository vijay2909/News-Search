import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from dateutil import parser
from datetime import timedelta
from .models import Keyword, NewsArticle

# Mapping of language codes to full names
LANGUAGE_MAP = {
    'ar': 'Arabic',
    'de': 'German',
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'he': 'Hebrew',
    'it': 'Italian',
    'nl': 'Dutch',
    'no': 'Norwegian',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'sv': 'Swedish',
    'zh': 'Chinese',
}

@login_required
def home(request):
    """
    Handles the main home page. Displays a search form and a list of the user's
    tracked keywords. Handles new keyword submissions.
    """
    if request.method == 'POST':
        keyword_text = request.POST.get('keyword', '').strip().lower()
        if not keyword_text:
            messages.error(request, "Please enter a keyword to search.")
            return redirect('home')

        # Prevent creating a duplicate keyword for the same user
        keyword, created = Keyword.objects.get_or_create(user=request.user, keyword=keyword_text)

        if created:
            messages.success(request, f"Now tracking new keyword: '{keyword.keyword}'.")
        else:
            messages.info(request, f"Showing results for existing keyword: '{keyword.keyword}'.")

        return redirect('keyword_articles', keyword_id=keyword.id)

    keywords = Keyword.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'news/home.html', {'keywords': keywords})


def _fetch_and_save_articles(keyword, fetch_only_new=False, language='en'):
    """
    Helper function to fetch articles from the API and save them.

    Args:
        keyword (Keyword): The keyword to search for.
        fetch_only_new (bool): If True, only fetches articles newer than the latest one stored.

    Returns:
        A tuple of (new_articles_found, error_message).
    """
    api_key = settings.NEWS_API_KEY
    if not api_key:
        # This message is for the server log, not for the user directly
        print("ERROR: News API key is not configured.")
        return 0, "News API key is not configured."

    url = (f'https://newsapi.org/v2/everything?'
           f'q="{keyword.keyword}"&'
           f'language={language}&'
           f'apiKey={api_key}&'
           f'sortBy=publishedAt')

    if fetch_only_new:
        latest_article = keyword.articles.order_by('-published_at').first()
        if latest_article:
            # Add 1 second to avoid re-fetching the same article
            from_date = (latest_article.published_at + timedelta(seconds=1)).isoformat()
            url += f'&from={from_date}'

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"API Request failed: {e}")
        return 0, f"Could not fetch news from the provider: {e}"

    new_articles_found = 0
    for article_data in data.get('articles', []):
        if not NewsArticle.objects.filter(url=article_data['url']).exists():
            try:
                # The 'publishedAt' field can sometimes be None
                if not article_data.get('publishedAt'):
                    continue

                published_time = parser.isoparse(article_data['publishedAt'])

                NewsArticle.objects.create(
                    keyword=keyword,
                    title=article_data['title'],
                    description=article_data.get('description'),
                    url=article_data['url'],
                    url_to_image=article_data.get('urlToImage'),
                    published_at=published_time,
                    source_name=article_data.get('source', {}).get('name', 'Unknown Source'),
                    language=language
                )
                new_articles_found += 1
            except Exception as e:
                print(f"Could not save article '{article_data.get('title')}': {e}")

    keyword.last_searched = timezone.now()
    keyword.save()
    return new_articles_found, None


@login_required
def keyword_articles(request, keyword_id):
    """
    Displays articles for a specific keyword. If no articles exist,
    it fetches them for the first time. Handles sorting of articles.
    """
    keyword = get_object_or_404(Keyword, id=keyword_id, user=request.user)

    # If this keyword has never been searched, fetch articles immediately
    # if keyword.last_searched is None:
    #     new_count, error_message = _fetch_and_save_articles(keyword)
    #     if error_message:
    #         messages.error(request, error_message)
    #     elif new_count > 0:
    #         messages.success(request, f"Found {new_count} articles for '{keyword.keyword}'.")
    #
    # articles_queryset = keyword.articles.all()

    # --- Filtering Logic ---
    filter_params = request.GET.copy()
    source_name = filter_params.get('source_name', '').strip()
    language = filter_params.get('language', 'en').strip() # Default to 'en'
    start_date = filter_params.get('start_date', '').strip()
    end_date = filter_params.get('end_date', '').strip()

    # Fetch articles for the selected language if they don't exist for this keyword
    if not keyword.articles.filter(language=language).exists():
        new_count, error_message = _fetch_and_save_articles(keyword, language=language)
        if error_message:
            messages.error(request, error_message)
        elif new_count > 0:
            messages.success(request,
                             f"Found {new_count} articles in {LANGUAGE_MAP.get(language, '')} for '{keyword.keyword}'.")

    articles_queryset = keyword.articles.all()

    if source_name:
        articles_queryset = articles_queryset.filter(source_name__icontains=source_name)
    if language:
        articles_queryset = articles_queryset.filter(language=language)
    if start_date:
        articles_queryset = articles_queryset.filter(published_at__gte=start_date)
    if end_date:
        articles_queryset = articles_queryset.filter(published_at__lte=end_date)

    # Sorting logic
    sort_option = request.GET.get('sort', 'newest')  # Default to 'newest'

    if sort_option == 'oldest':
        articles = articles_queryset.order_by('published_at')
    else:
        articles = articles_queryset.order_by('-published_at')

    context = {
        'keyword': keyword,
        'articles': articles,
        'current_sort': sort_option,
        'language_map': LANGUAGE_MAP,
        'filter_params': filter_params,  # Pass current filters back to template
    }
    return render(request, 'news/keyword_articles.html', context)


@login_required
def refresh_articles(request, keyword_id):
    """
    Deletes all existing articles for a keyword and fetches the latest ones.
    This includes a 15-minute throttle to prevent frequent API calls.
    """
    keyword = get_object_or_404(Keyword, id=keyword_id, user=request.user)
    language = request.GET.get('language', 'en')

    # --- Throttling Logic ---
    if keyword.last_searched:
        throttle_period = timedelta(minutes=15)
        time_since_last_search = timezone.now() - keyword.last_searched

        if time_since_last_search < throttle_period:
            minutes_left = int((throttle_period - time_since_last_search).total_seconds() / 60) + 1
            messages.warning(request,
                             f"You recently searched for this keyword. Please wait {minutes_left} more minute(s) before refreshing.")
            return redirect('keyword_articles', keyword_id=keyword.id)

    # --- Fetch only new articles ---
    messages.info(request, f"Checking for new articles for '{keyword.keyword}'...")
    new_count, error_message = _fetch_and_save_articles(keyword, fetch_only_new=True, language=language)

    if error_message:
        messages.error(request, error_message)
    elif new_count > 0:
        messages.success(request, f"Found {new_count} new articles.")
    else:
        messages.info(request, "No new articles found since the last search.")

    # Redirect back to the keyword articles page
    # Redirect back with the language filter preserved
    redirect_url = f"{redirect('keyword_articles', keyword_id=keyword.id).url}?language={language}"
    return redirect(redirect_url)
