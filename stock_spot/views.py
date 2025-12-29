from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from .models import Stock
from .serializers import StockSerializer
from .services.stock import StockService
from .services.alpha_vantage import AlphaVantageService
from .services.email import EmailService
import re


class StockViewSet(viewsets.ViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    lookup_field = 'symbol'
    lookup_url_kwarg = 'symbol'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stock_service = StockService()
        self.alpha_vantage_service = AlphaVantageService()

    @action(detail=False, methods=['post'])
    def create_stock(self, request):
        """Create a new stock with initial data from Alpha Vantage"""
        try:
            stock = self.stock_service.create_stock(
                name=request.data.get('name'),
                symbol=request.data.get('symbol'),
                is_bought=request.data.get('is_bought'),
                shares_owned=request.data.get('shares_owned')
            )
            serializer = self.get_serializer(stock)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def generate_daily_report(request):
    """Generate and send daily stock report"""
    try:
        # Parse comma-separated symbols from request
        symbols_input = request.data.get('symbols', '')
        if isinstance(symbols_input, str):
            # Split by comma and strip whitespace
            symbols = [s.strip().upper() for s in symbols_input.split(',') if s.strip()]
        else:
            symbols = symbols_input
        
        if not symbols:
            return Response(
                {'error': 'No stock symbols provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Send report
        email_service = EmailService()
        response = email_service.send_stock_report(symbols)
        
        if response.status_code == 200:
            return Response(
                {'message': 'Report generated and sent successfully', 'symbols': symbols},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': 'Failed to send email', 'details': response.text},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


def home_page(request):
    """Render the home page with stock report input"""
    from django.shortcuts import render
    return render(request, 'home.html')

