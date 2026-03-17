from django.db import models
from django.conf import settings
import json


class AnalysisHistory(models.Model):
    """Талдау тарихы"""
    LANGUAGE_CHOICES = [
        ('auto', 'Авто анықтау'),
        ('kk', 'Қазақша'),
        ('ru', 'Орысша'),
    ]
    
    text_snippet = models.TextField(max_length=200, verbose_name='Мәтін үзіндісі')
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='auto', verbose_name='Тіл')
    primary_emotion = models.CharField(max_length=50, verbose_name='Негізгі эмоция')
    confidence = models.FloatField(verbose_name='Сенімділік')
    probabilities = models.JSONField(verbose_name='Ықтималдылар')
    sentence_count = models.IntegerField(default=0, verbose_name='Сөйлем саны')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Құрылған уақыт')
    session_key = models.CharField(max_length=40, blank=True, verbose_name='Сессия кілті')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='analysis_histories',
        verbose_name='Пайдаланушы'
    )
    
    class Meta:
        verbose_name = 'Талдау тарихы'
        verbose_name_plural = 'Талдау тарихы'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.primary_emotion} ({self.confidence:.1%}) - {self.created_at.strftime('%d.%m.%Y %H:%M')}"


class Feedback(models.Model):
    """Кері байланыс"""
    FEEDBACK_CHOICES = [
        ('positive', '👍 Дұрыс'),
        ('negative', '👎 Қате'),
    ]
    
    analysis = models.ForeignKey(AnalysisHistory, on_delete=models.CASCADE, related_name='feedbacks', verbose_name='Талдау')
    feedback_type = models.CharField(max_length=10, choices=FEEDBACK_CHOICES, verbose_name='Кері байланыс түрі')
    comment = models.TextField(blank=True, verbose_name='Пікір')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Құрылған уақыт')
    
    class Meta:
        verbose_name = 'Кері байланыс'
        verbose_name_plural = 'Кері байланыс'
    
    def __str__(self):
        return f"{self.get_feedback_type_display()} - {self.analysis.primary_emotion}"


class EmotionModelInfo(models.Model):
    """Эмоция моделі туралы ақпарат"""
    name = models.CharField(max_length=100, verbose_name='Модель атауы')
    description = models.TextField(verbose_name='Сипаттама')
    emotions = models.JSONField(verbose_name='Эмоциялар тізімі')
    limitations = models.TextField(verbose_name='Шектеулер')
    is_active = models.BooleanField(default=True, verbose_name='Белсенді')
    
    class Meta:
        verbose_name = 'Модель ақпараты'
        verbose_name_plural = 'Модель ақпараты'
    
    def __str__(self):
        return self.name
