from django.contrib import admin
from .models import SosAlert

@admin.register(SosAlert)
class SosAlertAdmin(admin.ModelAdmin):
    list_display = ('id', 'latitude', 'longitude', 'status', 'created_at')
