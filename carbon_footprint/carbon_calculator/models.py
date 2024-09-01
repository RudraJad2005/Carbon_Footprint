from django.db import models

# Create your models here.
class DataPoint(models.Model):
    label = models.CharField(max_length=255)
    value = models.FloatField()

    def __str__(self):
        return f"{self.label}: {self.value}"