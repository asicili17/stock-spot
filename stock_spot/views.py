from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .models import Stock
from .serializers import StockSerializer
from .services.stock_profile_refresh_service import StockProfileRefreshService
from .services.alpha_vantage import AlphaVantageService
from .services.email import EmailService


class StockViewSet(viewsets.ViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    lookup_field = 'symbol'
    lookup_url_kwarg = 'symbol'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stock_service = StockProfileRefreshService()
        self.alpha_vantage_service = AlphaVantageService()

    @action(detail=False, methods=['post'])
    def create_stock(self, request):
        """Create a new stock with initial data from Alpha Vantage"""
        try:
            stock = self.stock_service.refresh(request.data.get('symbol'))
            serializer = self.get_serializer(stock)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def preview_stock_report(request):
    """Refresh requested symbols and return the email report HTML for preview."""
    try:
        symbols = _parse_symbols(request.data.get('symbols', ''))
        if not symbols:
            return Response(
                {'error': 'No stock symbols provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        email_service = EmailService()
        report = email_service.prepare_stock_report(symbols)
        return Response({
            'symbols': symbols,
            'report_date': report['report_date'],
            'report_html': email_service.render_stock_report(**report),
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def send_stock_report(request):
    """Email a previewed report to the address provided by the user."""
    try:
        symbols = _parse_symbols(request.data.get('symbols', ''))
        recipient_email = request.data.get('email', '').strip()
        if not symbols:
            return Response({'error': 'No stock symbols provided'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            validate_email(recipient_email)
        except ValidationError:
            return Response({'error': 'Enter a valid email address'}, status=status.HTTP_400_BAD_REQUEST)

        stocks = list(Stock.objects.filter(symbol__in=symbols))
        stocks_by_symbol = {stock.symbol: stock for stock in stocks}
        ordered_stocks = [stocks_by_symbol[symbol] for symbol in symbols if symbol in stocks_by_symbol]
        if not ordered_stocks:
            return Response({'error': 'Preview the report before sending it'}, status=status.HTTP_400_BAD_REQUEST)

        email_service = EmailService()
        response = email_service.send_stock_report(ordered_stocks, recipient_email)
        if response.status_code == 200:
            return Response(
                {'message': 'Report sent successfully', 'symbols': symbols},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': 'Failed to send email', 'details': response.text},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


def _parse_symbols(symbols_input):
    """Normalize a comma-separated symbol string or a list of symbols."""
    if isinstance(symbols_input, str):
        symbols = [symbol.strip().upper() for symbol in symbols_input.split(',') if symbol.strip()]
    elif isinstance(symbols_input, list):
        symbols = [str(symbol).strip().upper() for symbol in symbols_input if str(symbol).strip()]
    else:
        symbols = []
    return list(dict.fromkeys(symbols))


def home_page(request):
    """Render the home page with stock report input"""
    from django.shortcuts import render
    return render(request, 'home.html')

