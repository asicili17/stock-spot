from datetime import date
from stock_spot.models import Stock
from stock_spot.services.stock_profile_refresh_service import StockProfileRefreshService
import requests
from django.conf import settings
from django.template.loader import render_to_string

class EmailService:

    def __init__(self):
        self.base_url = settings.MAILGUN_BASE_URL
        self.domain = settings.MAILGUN_DOMAIN
        self.api_key = settings.MAILGUN_API_KEY
        self.from_email = settings.MAILGUN_FROM_EMAIL

    def prepare_stock_report(self, stock_symbols):
        """Refresh requested stocks and build the report used for preview and email."""
        report_date = date.today().strftime('%m-%d-%Y')
        stock_service = StockProfileRefreshService()
        stocks = []
        for symbol in stock_symbols:
            stock_service.refresh(symbol)
            stock = Stock.objects.filter(symbol=symbol).first()
            if stock:
                stocks.append(stock)

        return {
            'stocks': stocks,
            'report_date': report_date,
        }

    def render_stock_report(self, stocks, report_date):
        """Render the shared HTML report for a preview or an email."""
        context = {
            'stocks': stocks,
            'report_date': report_date,
        }
        return render_to_string('stock-spot-email.html', context)

    def send_stock_report(self, stocks, recipient_email, report_date=None):
        """Send a previously prepared report to a single recipient."""
        report_date = report_date or date.today().strftime('%m-%d-%Y')
        html_content = self.render_stock_report(stocks, report_date)
        
        return requests.post(
            f"{self.base_url}/v3/{self.domain}/messages",
            auth=("api", self.api_key),
            data={
                "from": "Stock Spot Application <" + self.from_email + ">",
                "to": recipient_email,
                "subject": f"Stock Report for {report_date}",
                "html": html_content,
                "text": f"Please find your stock report for {report_date} below."
            })
