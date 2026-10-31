from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StockViewSet, preview_stock_report, send_stock_report, home_page

router = DefaultRouter()
router.register(r'', StockViewSet)

urlpatterns = [
    path('home/', home_page, name='home'),
    path('api/', include(router.urls)),
    path('api/report/preview/', preview_stock_report, name='preview-stock-report'),
    path('api/report/send/', send_stock_report, name='send-stock-report'),
]
