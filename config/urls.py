"""
URL configuration for stock-spot project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from stock_spot.views import StockViewSet

router = DefaultRouter()
router.register(r'stocks', StockViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('rest_framework.urls')),
    path('api/stocks/', include('stock_spot.urls')),
    path('test/', TemplateView.as_view(template_name='stock_api_tester.html'), name='api_tester'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
