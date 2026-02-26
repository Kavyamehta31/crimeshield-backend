from django.urls import path
from .views import (
    police_login,
    create_complaint,
    check_complaint_status,
    get_all_complaints,
    update_complaint_status,
    police_create_complaint
)

urlpatterns = [
    path("login/", police_login),

    # Citizen APIs
    path("complaints/create/", create_complaint),
    path("complaints/status/", check_complaint_status),

    # Police Protected APIs
    path("complaints/all/", get_all_complaints),
    path("complaints/update-status/", update_complaint_status),
    path("complaints/police-create/", police_create_complaint),
]