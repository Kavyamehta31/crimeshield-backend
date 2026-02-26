from django.db import models
from django.contrib.auth.models import User
import secrets


class PoliceProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rank = models.CharField(max_length=50, default="Constable")
    station = models.CharField(max_length=100, default="Unknown")
    is_active = models.BooleanField(default=True)

    auth_token = models.CharField(max_length=128, blank=True, null=True)

    def generate_token(self):
        self.auth_token = secrets.token_hex(32)
        self.save()
        return self.auth_token

    def __str__(self):
        return self.user.username


# ==============================
# COMPLAINT MODEL (UPGRADED)
# ==============================

class Complaint(models.Model):

    citizen_name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=15)

    title = models.CharField(max_length=200)
    description = models.TextField()

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=[
            ("PENDING", "Pending"),
            ("IN_PROGRESS", "In Progress"),
            ("RESOLVED", "Resolved"),
        ],
        default="PENDING"
    )

    # ⭐ NEW FIELDS
    created_by_police = models.BooleanField(default=False)
    police_officer = models.CharField(max_length=100, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.citizen_name} - {self.title} ({self.status})"