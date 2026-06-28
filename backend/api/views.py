import json
import os
import random
from datetime import datetime, timedelta, timezone

from django.conf import settings as djs
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import User, Charity, VolunteerProfile, VolunteerInterest, VerificationCode

MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_MIME  = {"image/jpeg", "image/png"}
ALLOWED_EXT   = {".jpg", ".jpeg", ".png"}


def _validate_image(file, field="file"):
    if file.content_type not in ALLOWED_MIME:
        return f"Only JPG and PNG images are allowed for {field}"
    if os.path.splitext(file.name)[1].lower() not in ALLOWED_EXT:
        return f"Only JPG and PNG images are allowed for {field}"
    if file.size > MAX_FILE_SIZE:
        return f"{field.capitalize()} exceeds the 5 MB maximum size"
    return None


def _gen_code():
    return str(random.randint(100000, 999999))


def _parse_json(request):
    try:
        return json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return None


# POST /api/auth/register/volunteer
@csrf_exempt
@require_POST
def register_volunteer(request):
    data = _parse_json(request)
    if data is None:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    first_name = (data.get("firstName") or "").strip()
    surname    = (data.get("surname")   or "").strip()
    email      = (data.get("email")     or "").strip().lower()
    password   = (data.get("password")  or "")
    phone      = (data.get("phone")     or "").strip() or None
    age_raw    = data.get("age")

    if not all([first_name, surname, email, password]):
        return JsonResponse({"error": "First name, surname, email and password are required"}, status=400)
    if len(password) < 8:
        return JsonResponse({"error": "Password must be at least 8 characters long"}, status=400)

    age = None
    if age_raw not in (None, ""):
        try:
            age = int(age_raw)
            if not (16 <= age <= 99):
                return JsonResponse({"error": "Age must be between 16 and 99"}, status=400)
        except (ValueError, TypeError):
            return JsonResponse({"error": "Invalid age"}, status=400)

    if User.objects.filter(email=email).exists():
        return JsonResponse({"error": "This email address is already registered"}, status=409)

    user = User.objects.create(
        role="volunteer", email=email,
        password=make_password(password),
        first_name=first_name, surname=surname, age=age, phone=phone,
    )
    code = _gen_code()
    VerificationCode.objects.create(
        user=user, code=code,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )

    print(f"\n{'='*40}")
    print(f"  [VERIFICATION CODE]")
    print(f"  Email : {email}")
    print(f"  Code  : {code}")
    print(f"{'='*40}\n")

    return JsonResponse({
        "message": "Registration successful. Check the server console for the code.",
        "userId": user.id,
        "devCode": code,
    }, status=201)


# POST /api/auth/register/charity
@csrf_exempt
@require_POST
def register_charity(request):
    org       = (request.POST.get("org")       or "").strip()
    edrpou    = (request.POST.get("edrpou")    or "").strip()
    org_email = (request.POST.get("orgEmail")  or "").strip().lower()
    password  = (request.POST.get("password")  or "")
    cp_first  = (request.POST.get("cpFirst")   or "").strip()
    cp_surn   = (request.POST.get("cpSurname") or "").strip()
    cp_phone  = (request.POST.get("cpPhone")   or "").strip() or None
    cp_email  = (request.POST.get("cpEmail")   or "").strip() or None
    logo_file = request.FILES.get("logo")

    if not all([org, edrpou, org_email, password]):
        return JsonResponse({"error": "Organisation name, EDRPOU, email and password are required"}, status=400)
    if not edrpou.isdigit() or len(edrpou) != 8:
        return JsonResponse({"error": "EDRPOU must be an 8-digit number"}, status=400)
    if len(password) < 8:
        return JsonResponse({"error": "Password must be at least 8 characters long"}, status=400)

    if logo_file:
        err = _validate_image(logo_file, "logo")
        if err:
            return JsonResponse({"error": err}, status=400)

    if User.objects.filter(email=org_email).exists():
        return JsonResponse({"error": "This email address is already registered"}, status=409)
    if Charity.objects.filter(edrpou=edrpou).exists():
        return JsonResponse({"error": "This EDRPOU is already registered"}, status=409)

    user = User.objects.create(
        role="charity", email=org_email,
        password=make_password(password),
        first_name=cp_first or None, surname=cp_surn or None, phone=cp_phone,
    )
    Charity.objects.create(
        user=user, org_name=org, edrpou=edrpou,
        contact_first=cp_first, contact_surname=cp_surn,
        contact_phone=cp_phone, contact_email=cp_email,
        logo=logo_file,
    )
    code = _gen_code()
    VerificationCode.objects.create(
        user=user, code=code,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )

    print(f"\n{'='*40}")
    print(f"  [VERIFICATION CODE]")
    print(f"  Email : {org_email}")
    print(f"  Code  : {code}")
    print(f"{'='*40}\n")

    return JsonResponse({
        "message": "Registration successful. Check the server console for the code.",
        "userId": user.id,
        "devCode": code,
    }, status=201)


# POST /api/auth/verify
@csrf_exempt
@require_POST
def verify_email(request):
    data = _parse_json(request)
    if data is None:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    user_id = data.get("userId")
    code    = str(data.get("code", "")).strip()

    if not user_id or not code:
        return JsonResponse({"error": "userId and code are required"}, status=400)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    record = VerificationCode.objects.filter(user=user, code=code, used=False).order_by("-id").first()
    if not record:
        return JsonResponse({"error": "Invalid verification code"}, status=400)
    if record.expires_at < datetime.now(timezone.utc):
        return JsonResponse({"error": "Code expired. Request a new one."}, status=400)

    user.verified = True
    user.save(update_fields=["verified"])
    record.used = True
    record.save(update_fields=["used"])
    return JsonResponse({"message": "Email verified successfully", "role": user.role})


# POST /api/auth/resend
@csrf_exempt
@require_POST
def resend_code(request):
    data = _parse_json(request)
    if data is None:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    user_id = data.get("userId")
    if not user_id:
        return JsonResponse({"error": "userId is required"}, status=400)

    try:
        user = User.objects.get(id=user_id, verified=False)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found or already verified"}, status=404)

    code = _gen_code()
    VerificationCode.objects.create(
        user=user, code=code,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )

    print(f"\n{'='*40}")
    print(f"  [VERIFICATION CODE] (resent)")
    print(f"  Email : {user.email}")
    print(f"  Code  : {code}")
    print(f"{'='*40}\n")

    return JsonResponse({"message": "A new code has been sent", "devCode": code})


# POST /api/profile/update
@csrf_exempt
@require_POST
def update_profile(request):
    user_id     = request.POST.get("userId")
    city        = (request.POST.get("city") or "").strip() or None
    interests   = request.POST.getlist("interests")
    avatar_file = request.FILES.get("avatar")

    if not user_id:
        return JsonResponse({"error": "userId is required"}, status=400)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    if avatar_file:
        err = _validate_image(avatar_file, "avatar")
        if err:
            return JsonResponse({"error": err}, status=400)

    profile, _ = VolunteerProfile.objects.get_or_create(user=user)
    profile.city = city
    if avatar_file:
        profile.avatar = avatar_file
    profile.save()

    VolunteerInterest.objects.filter(user=user).delete()
    for interest in interests:
        interest = interest.strip()
        if interest:
            VolunteerInterest.objects.create(user=user, interest=interest)

    return JsonResponse({"message": "Profile updated successfully"})


# GET /api/profile/<user_id>
def get_profile(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    data = {
        "id": user.id, "role": user.role, "email": user.email,
        "first_name": user.first_name, "surname": user.surname,
        "age": user.age, "phone": user.phone, "verified": user.verified,
    }
    try:
        p = user.volunteer_profile
        data["city"]   = p.city
        data["avatar"] = p.avatar.url if p.avatar else None
    except VolunteerProfile.DoesNotExist:
        data["city"] = data["avatar"] = None

    data["interests"] = list(
        VolunteerInterest.objects.filter(user=user).values_list("interest", flat=True)
    )
    if user.role == "charity":
        try:
            c = user.charity
            data["charity"] = {
                "org_name": c.org_name,
                "edrpou":   c.edrpou,
                "logo":     c.logo.url if c.logo else None,
            }
        except Charity.DoesNotExist:
            data["charity"] = None
    return JsonResponse(data)
