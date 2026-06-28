import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-dev-key-replace-in-production-volunteerhub'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'corsheaders',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'api',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'volunteerhub.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'volunteerhub.db',
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_ROOT = BASE_DIR / 'uploads'
MEDIA_URL = '/uploads/'

FRONTEND_DIR = BASE_DIR.parent / 'frontend_src' / 'VolunteerHub' / 'frontend_src'

CORS_ALLOW_ALL_ORIGINS = True
APPEND_SLASH = False

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_TZ = True

# ── Email (Gmail SMTP) ────────────────────────────────────────────────────────
# Заповни EMAIL_HOST_USER і EMAIL_HOST_PASSWORD, тоді листи підуть на пошту.
# EMAIL_HOST_PASSWORD — це App Password з Google (не звичайний пароль).
# Якщо залишити порожніми — код виводиться тільки в консоль.
EMAIL_BACKEND     = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST        = 'smtp.gmail.com'
EMAIL_PORT        = 587
EMAIL_USE_TLS     = True
EMAIL_HOST_USER   = ''          # ← твій gmail: example@gmail.com
EMAIL_HOST_PASSWORD = ''        # ← App Password з Google
DEFAULT_FROM_EMAIL = 'Dobrodiy <noreply@dobrodiy.ua>'
