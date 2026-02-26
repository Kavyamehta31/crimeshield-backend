from rest_framework import serializers
from .models import SosAlert

class SosAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = SosAlert
        fields = ['id', 'latitude', 'longitude', 'status', 'created_at']
