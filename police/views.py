from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import localtime
from .models import Complaint, PoliceProfile
import json


# =====================================
# 🔐 TOKEN VALIDATION FUNCTION
# =====================================

def validate_police_token(request):
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return None

    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ")[1]

    try:
        profile = PoliceProfile.objects.get(auth_token=token)
        return profile
    except PoliceProfile.DoesNotExist:
        return None


# =====================================
# 🔐 POLICE LOGIN (TOKEN BASED)
# =====================================

@csrf_exempt
def police_login(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")

        user = authenticate(username=username, password=password)

        if user is None:
            return JsonResponse({"error": "Invalid credentials"}, status=401)

        if not user.groups.filter(name="Police").exists():
            return JsonResponse({"error": "Not authorized as police"}, status=403)

        profile = PoliceProfile.objects.get(user=user)

        token = profile.generate_token()

        return JsonResponse({
            "message": "Police login successful",
            "username": user.username,
            "token": token
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# =====================================
# 📄 CREATE COMPLAINT (PUBLIC)
# =====================================

@csrf_exempt
def create_complaint(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)

        citizen_name = data.get("citizen_name")
        mobile_number = data.get("mobile_number")
        title = data.get("title")
        description = data.get("description")
        latitude = data.get("latitude")
        longitude = data.get("longitude")

        if not citizen_name or not mobile_number or not title or not description:
            return JsonResponse({"error": "Missing required fields"}, status=400)

        complaint = Complaint.objects.create(
            citizen_name=citizen_name,
            mobile_number=mobile_number,
            title=title,
            description=description,
            latitude=latitude,
            longitude=longitude
        )

        return JsonResponse({
            "message": "Complaint submitted successfully",
            "complaint_id": complaint.id
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# =====================================
# 📊 CHECK COMPLAINT STATUS (PUBLIC)
# =====================================

@csrf_exempt
def check_complaint_status(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    data = json.loads(request.body)
    mobile = data.get("mobile_number")

    if not mobile:
        return JsonResponse({"error": "Mobile number required"}, status=400)

    complaints = Complaint.objects.filter(
        mobile_number=mobile
    ).order_by("-created_at")

    result = []

    for c in complaints:
        local_created = localtime(c.created_at)

        result.append({
            "id": c.id,
            "title": c.title,
            "status": c.status,
            "created_at": local_created.strftime("%d %b %Y, %I:%M %p")
        })

    return JsonResponse({"complaints": result})


# =====================================
# 🗄 POLICE: VIEW ALL COMPLAINTS (PROTECTED)
# =====================================

@csrf_exempt
def get_all_complaints(request):

    if request.method != "GET":
        return JsonResponse({"error": "GET required"}, status=405)

    profile = validate_police_token(request)

    if not profile:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    complaints = Complaint.objects.all().order_by("-created_at")

    result = []

    for c in complaints:
        local_created = localtime(c.created_at)

        result.append({
            "id": c.id,
            "citizen_name": c.citizen_name,
            "mobile_number": c.mobile_number,
            "title": c.title,
            "description": c.description,
            "status": c.status,
            "latitude": c.latitude,
            "longitude": c.longitude,
            "created_at": local_created.strftime("%d %b %Y, %I:%M %p")
        })

    return JsonResponse({"complaints": result})
@csrf_exempt
def update_complaint_status(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    # 🔐 Validate token
    profile = validate_police_token(request)

    if not profile:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    try:
        data = json.loads(request.body)

        complaint_id = data.get("complaint_id")
        new_status = data.get("status")

        if not complaint_id or not new_status:
            return JsonResponse({"error": "Missing fields"}, status=400)

        if new_status not in ["PENDING", "IN_PROGRESS", "RESOLVED"]:
            return JsonResponse({"error": "Invalid status"}, status=400)

        complaint = Complaint.objects.get(id=complaint_id)
        complaint.status = new_status
        complaint.save()

        return JsonResponse({
            "message": "Status updated successfully"
        })

    except Complaint.DoesNotExist:
        return JsonResponse({"error": "Complaint not found"}, status=404)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    # ==============================
# POLICE CREATE COMPLAINT (PROTECTED)
# ==============================

@csrf_exempt
def police_create_complaint(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    profile = validate_police_token(request)

    if not profile:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    try:
        data = json.loads(request.body)

        citizen_name = data.get("citizen_name")
        mobile_number = data.get("mobile_number")
        title = data.get("title")
        description = data.get("description")
        latitude = data.get("latitude")
        longitude = data.get("longitude")

        if not citizen_name or not mobile_number or not title or not description:
            return JsonResponse({"error": "Missing required fields"}, status=400)

        complaint = Complaint.objects.create(
            citizen_name=citizen_name,
            mobile_number=mobile_number,
            title=title,
            description=description,
            latitude=latitude,
            longitude=longitude,
            created_by_police=True,
            police_officer=profile.user.username
        )

        return JsonResponse({
            "message": "Complaint created by police successfully",
            "complaint_id": complaint.id
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)