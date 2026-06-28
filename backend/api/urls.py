from django.urls import path
from . import views

urlpatterns = [
    path("auth/register/volunteer", views.register_volunteer),
    path("auth/register/charity",   views.register_charity),
    path("auth/verify",             views.verify_email),
    path("auth/resend",             views.resend_code),
    path("profile/update",          views.update_profile),
    path("profile/<int:user_id>",   views.get_profile),
]
