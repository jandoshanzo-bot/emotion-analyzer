from django.contrib import admin
from .models import AnalysisHistory, Feedback, EmotionModelInfo


@admin.register(AnalysisHistory)
class AnalysisHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'text_snippet', 'primary_emotion', 'confidence_percent', 'language', 'created_at']
    list_filter = ['primary_emotion', 'language', 'created_at']
    search_fields = ['text_snippet', 'primary_emotion']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    def confidence_percent(self, obj):
        return f"{obj.confidence:.1%}"
    confidence_percent.short_description = 'Сенімділік'


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['id', 'analysis', 'feedback_type', 'created_at']
    list_filter = ['feedback_type', 'created_at']
    readonly_fields = ['created_at']
    ordering = ['-created_at']


@admin.register(EmotionModelInfo)
class EmotionModelInfoAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
