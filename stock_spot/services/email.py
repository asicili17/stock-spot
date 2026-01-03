from datetime import date
from stock_spot.models import Stock
from stock_spot.services.stock import StockService
import requests
from django.conf import settings
from django.template.loader import render_to_string

class EmailService:

    def __init__(self):
        self.base_url = settings.MAILGUN_BASE_URL
        self.domain = settings.MAILGUN_DOMAIN
        self.api_key = settings.MAILGUN_API_KEY
        self.from_email = settings.MAILGUN_FROM_EMAIL
        self.distribution_list = settings.EMAIL_DISTRIBUTION_LIST

    def send_stock_report(self, stock_symbols):
        """Send stock report email with table of stocks."""
        report_date = date.today().strftime('%m-%d-%Y')
        stock_service = StockService()
        stocks = []
        # Fetch stock data from API and populate stocks list
        for symbol in stock_symbols:
            stock_service.create_stock(symbol)
            stock = Stock.objects.filter(symbol=symbol).first()
            stocks.append(stock)

        # Render HTML template
        context = {
            'stocks': stocks,
            'report_date': report_date,
        }
        html_content = render_to_string('stock-spot-email.html', context)
        
        return requests.post(
            f"{self.base_url}/v3/{self.domain}/messages",
            auth=("api", self.api_key),
            data={
                "from": "Stock Spot Application <" + self.from_email + ">",
                "to": self.distribution_list,
                "subject": f"Stock Report for {report_date}",
                "html": html_content,
                "text": f"Please find your stock report for {report_date} below."
            })