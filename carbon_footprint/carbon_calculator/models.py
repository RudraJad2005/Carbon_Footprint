from django.db import models
from django.utils import timezone
# Create your models here.
class DataPoint(models.Model):
    label = models.CharField(max_length=255)
    value = models.FloatField()

    def __str__(self):
        return f"{self.label}: {self.value}"
    

class CarbonFootprintHistory(models.Model):
    user = models.CharField(max_length=100)
    electricity = models.FloatField()
    natural_gas = models.FloatField()
    biomass = models.FloatField()
    coal = models.FloatField()
    heating_oil = models.FloatField()
    lpg = models.FloatField()
    total_co2e = models.FloatField()
    created_at = models.DateTimeField(default=timezone.now)  # Automatically set to now on record creation

    def __str__(self):
        return f"{self.user} - {self.total_co2e} CO2e on {self.created_at}"