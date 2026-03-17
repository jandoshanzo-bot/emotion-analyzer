from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Django аутентификациясы: /accounts/login/, /accounts/logout/ және т.б.
    path('accounts/', include('django.contrib.auth.urls')),

    # Analyzer қолданбасы (`namespace='analyzer'` үшін)
    path('', include(('analyzer.urls', 'analyzer'), namespace='analyzer')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
