from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.db.models import Count
from django import forms
from .models import Keyword, NewsArticle


class CustomIntervalForm(forms.Form):
    """A form for setting a custom refresh interval on a keyword."""
    keyword_text = forms.CharField(label="Keyword Text", max_length=100)
    interval = forms.IntegerField(
        label="Refresh Interval (in seconds)",
        min_value=300,  # e.g., minimum 5 minutes
        help_text="Set a custom refresh interval. Must be at least 300 seconds."
    )


@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ('keyword', 'user', 'last_searched', 'custom_refresh_interval')
    search_fields = ('keyword', 'user__username')

    def get_urls(self):
        """Adds the custom dashboard URL to the admin URLs."""
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_site.admin_view(self.dashboard_view), name='keyword_dashboard'),
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        """The view for the custom admin dashboard."""
        if request.method == 'POST':
            form = CustomIntervalForm(request.POST)
            if form.is_valid():
                keyword_text = form.cleaned_data['keyword_text']
                interval = form.cleaned_data['interval']

                # Update all keywords with this text across all users
                updated_count = Keyword.objects.filter(text__iexact=keyword_text).update(
                    custom_refresh_interval=interval)

                if updated_count > 0:
                    self.message_user(request,
                                      f"Successfully set custom interval for '{keyword_text}' ({updated_count} user instances).")
                else:
                    self.message_user(request, f"No keywords found for '{keyword_text}'.", level='warning')
                return redirect('.')
        else:
            form = CustomIntervalForm()

        # Calculate trending keywords (most users tracking the same keyword text)
        trending_keywords = Keyword.objects.values('text').annotate(
            user_count=Count('user', distinct=True)
        ).order_by('-user_count')[:10]

        context = dict(
            self.admin_site.each_context(request),
            trending_keywords=trending_keywords,
            form=form,
            title="Keywords Dashboard"
        )
        return render(request, "admin/keyword_dashboard.html", context)


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'keyword', 'source_name', 'language', 'published_at')
    list_filter = ('language', 'source_name', 'keyword')
    search_fields = ('title', 'keyword__keyword')
