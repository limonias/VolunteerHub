from django.urls import path
from . import views

urlpatterns = [
    path("auth/register/volunteer", views.register_volunteer, name="register_volunteer"),
    path("auth/register/charity",   views.register_charity, name="register_charity"),
    path("auth/verify",             views.verify_email, name="verify_email"),
    path("auth/resend",             views.resend_code, name="resend_code"),
    path("profile/update",          views.update_profile, name="update_profile"),
    path("profile/me",              views.get_my_profile, name="get_my_profile"),
    path("profile/<int:user_id>",   views.get_profile, name="get_profile"),
]
