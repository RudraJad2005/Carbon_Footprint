from django.contrib import admin
from .models import CarbonFootprintHistory

# Register your models here.
@admin.register(CarbonFootprintHistory)
class CarbonFootprintHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_co2e', 'electricity', 'natural_gas', 'biomass', 'coal', 'heating_oil', 'lpg']