from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StockViewSet, generate_daily_report, home_page

router = DefaultRouter()
router.register(r'', StockViewSet)

urlpatterns = [
    path('home/', home_page, name='home'),
    path('api/', include(router.urls)),
    path('api/report/', generate_daily_report, name='generate-daily-report'),
]