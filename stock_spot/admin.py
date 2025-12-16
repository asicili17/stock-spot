from django.contrib import admin
from .models import Stock, AnnualEarning, QuarterlyEarning

admin.site.register(Stock)
admin.site.register(AnnualEarning)
admin.site.register(QuarterlyEarning)
