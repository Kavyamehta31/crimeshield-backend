from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
from django.utils.timezone import localtime

from .models import SosAlert
from police.views import validate_police_token

import json


# ==========================================
# 🚨 START SOS (PUBLIC)
# ==========================================

@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def start_sos(request):

    latitude = request.data.get("latitude")
    longitude = request.data.get("longitude")
    citizen_name = request.data.get("citizen_name")
    citizen_mobile = request.data.get("citizen_mobile")

    if not latitude or not longitude:
        return Response({"error": "Location missing"}, status=400)

    sos = SosAlert.objects.create(
        latitude=latitude,
        longitude=longitude,
        status="ACTIVE",
        created_at=timezone.now(),
        citizen_name=citizen_name,
        citizen_mobile=citizen_mobile
    )

    return Response({
        "message": "SOS created",
        "sos_id": sos.id
    })


# ==========================================
# 🎥 UPLOAD VIDEO (PUBLIC)
# ==========================================

@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def upload_video(request):

    video = request.FILES.get("video")

    if not video:
        return Response({"error": "No video received"}, status=400)

    sos = SosAlert.objects.filter(status="ACTIVE").order_by("-id").first()

    if not sos:
        return Response({"error": "No active SOS"}, status=404)

    sos.video = video
    sos.save()

    return Response({"message": "Video uploaded successfully"})


# ==========================================
# 📱 GET SOS BY MOBILE (PUBLIC)
# ==========================================

@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def get_sos_by_mobile(request):

    mobile = request.data.get("mobile_number")

    if not mobile:
        return Response({"error": "Mobile number required"}, status=400)

    sos_list = SosAlert.objects.filter(
        citizen_mobile=mobile
    ).order_by("-created_at")

    result = []

    for s in sos_list:
        local_created = localtime(s.created_at)

        result.append({
            "id": s.id,
            "status": s.status,
            "created_at": local_created.strftime("%d %b %Y, %I:%M %p"),
            "video": s.video.url if s.video else None
        })

    return Response({"sos": result})


# ==========================================
# 🗄 POLICE: VIEW ALL SOS (PROTECTED)
# ==========================================
@csrf_exempt
def get_all_sos(request):

    if request.method != "GET":
        return JsonResponse({"error": "GET required"}, status=405)

    profile = validate_police_token(request)

    if not profile:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    sos_list = SosAlert.objects.all().order_by("-created_at")

    result = []

    for s in sos_list:
        local_created = localtime(s.created_at)

        result.append({
            "id": s.id,
            "citizen_name": s.citizen_name,
            "citizen_mobile": s.citizen_mobile,
            "status": s.status,
            "latitude": s.latitude,
            "longitude": s.longitude,
            "video": s.video.url if s.video else None,
            "created_at": local_created.strftime("%d %b %Y, %I:%M %p")
        })

    return JsonResponse({"sos": result})


# ==========================================
# 🔄 POLICE: UPDATE SOS STATUS (PROTECTED)
# ==========================================

@csrf_exempt
def update_sos_status(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    profile = validate_police_token(request)

    if not profile:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    try:
        data = json.loads(request.body)

        sos_id = data.get("sos_id")
        new_status = data.get("status")

        if not sos_id or not new_status:
            return JsonResponse({"error": "Missing fields"}, status=400)

        if new_status not in ["ACTIVE", "IN_PROGRESS", "RESOLVED"]:
            return JsonResponse({"error": "Invalid status"}, status=400)

        sos = SosAlert.objects.get(id=sos_id)
        sos.status = new_status
        sos.save()

        return JsonResponse({"message": "SOS status updated successfully"})

    except SosAlert.DoesNotExist:
        return JsonResponse({"error": "SOS not found"}, status=404)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)