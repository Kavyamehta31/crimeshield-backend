from django.urls import path
from .views import (
    start_sos,
    upload_video,
    get_sos_by_mobile,
    get_all_sos,
    update_sos_status
)

urlpatterns = [
    path("start/", start_sos),
    path("upload-video/", upload_video),
    path("status/", get_sos_by_mobile),
    path("all/", get_all_sos),
    path("update-status/", update_sos_status),
]