from django.db import models

class Dataset(models.Model):
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    total_equipment = models.IntegerField()
    avg_flowrate = models.FloatField()
    max_pressure = models.FloatField()
    min_temperature = models.FloatField()
    max_temperature = models.FloatField()
