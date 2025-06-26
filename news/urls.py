from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('keyword/<int:keyword_id>/', views.keyword_articles, name='keyword_articles'),
    path('keyword/<int:keyword_id>/refresh/', views.refresh_articles, name='refresh_articles'),
    # path('search/', views.search_news, name='search_news'),
    # path('history/', views.search_history, name='search_history'),
    # path('refresh/<int:keyword_id>/', views.refresh_keyword, name='refresh_keyword'),
    # path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    # path('admin/toggle-user/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),
    # path('admin/update-quota/<int:user_id>/', views.update_user_quota, name='update_user_quota'),
    # path('register/', views.register, name='register'),
]