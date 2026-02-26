from django.db import models


class SosAlert(models.Model):

    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("IN_PROGRESS", "In Progress"),
        ("RESOLVED", "Resolved"),
    ]

    latitude = models.FloatField()
    longitude = models.FloatField()

    video = models.FileField(
        upload_to='sos_videos/',
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="ACTIVE"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    citizen_name = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    citizen_mobile = models.CharField(
        max_length=15,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.citizen_name} - {self.status}"