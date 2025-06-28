from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('keyword/<int:keyword_id>/', views.keyword_articles, name='keyword_articles'),
    path('keyword/<int:keyword_id>/refresh/', views.refresh_articles, name='refresh_articles'),
]