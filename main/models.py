from django.db import models


class dataRecivedModel(models.Model):
    heartRate = models.CharField(max_length=64, default="0")  # Default value
    spo2 = models.CharField(max_length=64, default="0")  # Default value
    humidity = models.CharField(max_length=64, default="0")  # Default value
    temprature = models.CharField(max_length=64, default="0")  # Default value
    tempratureBody = models.CharField(max_length=64, default="0")  # Default value

    def __str__(self):
        return f"Heart Rate: {self.heartRate}, SpO2: {self.spo2}"
