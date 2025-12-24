from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Stock
from .serializers import StockSerializer
from .services.stock import StockService
from .services.alpha_vantage import AlphaVantageService


class StockViewSet(viewsets.ModelViewSet):
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

    @action(detail=True, methods=['post'])
    def fetch_rsi(self, request, symbol=None):
        """Fetch and update RSI data for a specific stock"""
        try:
            stock = self.get_object()
            self.alpha_vantage_service.get_relative_strength_index_data(stock.symbol)
            stock.refresh_from_db()
            serializer = self.get_serializer(stock)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def fetch_eps(self, request, symbol=None):
        """Fetch and update EPS data for a specific stock"""
        try:
            stock = self.get_object()
            self.alpha_vantage_service.get_eps_change(stock.symbol)
            stock.refresh_from_db()
            serializer = self.get_serializer(stock)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
