from django.urls import path
from . import views

app_name = 'analyzer'

urlpatterns = [
    path('', views.home, name='home'),
    path('history/', views.history, name='history'),
    path('about/', views.about, name='about'),
    path('register/', views.register, name='register'),

    path('api/predict/', views.api_predict, name='api_predict'),
    path('api/history/stats/', views.api_history_stats, name='api_history_stats'),
    path('api/history/clear/', views.api_history_clear, name='api_history_clear'),
    path('api/history/<int:analysis_id>/', views.api_history_detail, name='api_history_detail'),
    path('api/history/<int:analysis_id>/delete/', views.api_history_delete, name='api_history_delete'),
    path('api/history/delete/<int:analysis_id>/', views.api_history_delete, name='api_history_delete_legacy'),
]
