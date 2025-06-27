import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
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
    tracked keywords. Enforces a quota on the number of keywords a user can track.
    """
    if request.method == 'POST':
        keyword_text = request.POST.get('keyword', '').strip().lower()
        language = request.POST.get('language', 'en')

        if not keyword_text:
            messages.error(request, "Please enter a keyword to search.")
            return redirect('home')

        # --- Keyword Quota Logic ---
        # Check if the keyword already exists for this user.
        keyword_exists = Keyword.objects.filter(user=request.user, keyword=keyword_text).exists()

        # If the keyword is new, check if the user is under their quota.
        if not keyword_exists:
            current_keyword_count = Keyword.objects.filter(user=request.user).count()
            quota = request.user.profile.keyword_quota
            if current_keyword_count >= quota:
                messages.error(request,
                               f"You have reached your keyword limit of {quota}. You cannot add more keywords.")
                return redirect('home')

        # Proceed with get_or_create, which is safe now.
        keyword, created = Keyword.objects.get_or_create(user=request.user, keyword=keyword_text)

        if created:
            messages.success(request, f"Now tracking new keyword: '{keyword.keyword}'.")
        else:
            messages.info(request, f"Showing results for existing keyword: '{keyword.keyword}'.")

        redirect_url = f"{reverse('keyword_articles', args=[keyword.id])}?language={language}"
        return redirect(redirect_url)

    keywords = Keyword.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'keywords': keywords,
        'language_map': LANGUAGE_MAP,
    }
    return render(request, 'news/home.html', context)


def _fetch_and_save_articles(keyword, fetch_only_new=False, language='en'):
    """
    Helper function to fetch articles from the API and save them.
    """
    api_key = settings.NEWS_API_KEY
    if not api_key:
        print("ERROR: News API key is not configured.")
        return 0, "News API key is not configured."

    url = (f'https://newsapi.org/v2/everything?'
           f'q="{keyword.keyword}"&'
           f'language={language}&'
           f'apiKey={api_key}&'
           f'sortBy=publishedAt')

    if fetch_only_new:
        latest_article = keyword.articles.filter(language=language).order_by('-published_at').first()
        if latest_article:
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
    Displays articles for a specific keyword, with sorting and filtering.
    """
    keyword = get_object_or_404(Keyword, id=keyword_id, user=request.user)

    filter_params = request.GET.copy()
    language = filter_params.get('language', 'en').strip()

    if not keyword.articles.filter(language=language).exists():
        new_count, error_message = _fetch_and_save_articles(keyword, language=language)
        if error_message:
            messages.error(request, error_message)
        elif new_count > 0:
            messages.success(request,
                             f"Found {new_count} articles in {LANGUAGE_MAP.get(language, '')} for '{keyword.keyword}'.")

    articles_queryset = keyword.articles.all()
    source_name = filter_params.get('source_name', '').strip()
    start_date = filter_params.get('start_date', '').strip()
    end_date = filter_params.get('end_date', '').strip()

    if source_name:
        articles_queryset = articles_queryset.filter(source_name__icontains=source_name)
    if language:
        articles_queryset = articles_queryset.filter(language=language)
    if start_date:
        articles_queryset = articles_queryset.filter(published_at__gte=start_date)
    if end_date:
        articles_queryset = articles_queryset.filter(published_at__lte=end_date)

    sort_option = filter_params.get('sort', 'newest')
    if sort_option == 'oldest':
        articles = articles_queryset.order_by('published_at')
    else:
        articles = articles_queryset.order_by('-published_at')

    context = {
        'keyword': keyword,
        'articles': articles,
        'current_sort': sort_option,
        'language_map': LANGUAGE_MAP,
        'filter_params': filter_params,
    }
    return render(request, 'news/keyword_articles.html', context)


@login_required
def refresh_articles(request, keyword_id):
    """
    Fetches only new articles since the last search for the specified language.
    """
    keyword = get_object_or_404(Keyword, id=keyword_id, user=request.user)
    language = request.GET.get('language', 'en')

    if keyword.last_searched:
        throttle_period = timedelta(minutes=15)
        time_since_last_search = timezone.now() - keyword.last_searched

        if time_since_last_search < throttle_period:
            minutes_left = int((throttle_period - time_since_last_search).total_seconds() / 60) + 1
            messages.warning(request, f"You recently searched. Please wait {minutes_left} more minute(s).")
            return redirect('keyword_articles', keyword_id=keyword.id)

    messages.info(request, f"Checking for new articles in {LANGUAGE_MAP.get(language, '')} for '{keyword.keyword}'...")
    new_count, error_message = _fetch_and_save_articles(keyword, fetch_only_new=True, language=language)

    if error_message:
        messages.error(request, error_message)
    elif new_count > 0:
        messages.success(request, f"Found {new_count} new articles.")
    else:
        messages.info(request, "No new articles found since the last search.")

    redirect_url = f"{reverse('keyword_articles', args=[keyword.id])}?language={language}"
    return redirect(redirect_url)
