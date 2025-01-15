from rest_framework import serializers

from .models import dataRecivedModel


class DataReceivedSerializer(serializers.ModelSerializer):
    class Meta:
        model = dataRecivedModel
        fields = '__all__'
