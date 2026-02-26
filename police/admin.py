from django.contrib import admin
from .models import PoliceProfile, Complaint


@admin.register(PoliceProfile)
class PoliceProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'rank', 'station', 'is_active')


# ==============================
# COMPLAINT ADMIN CONFIG
# ==============================

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = (
        "citizen_name",
        "mobile_number",
        "title",
        "status",
        "created_at"
    )

    list_filter = ("status", "created_at")
    search_fields = ("citizen_name", "mobile_number", "title")
    ordering = ("-created_at",)