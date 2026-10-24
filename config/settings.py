"""Django settings for the Supplyhive stationery shop project."""

import os
from decimal import Decimal
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent


def env_list(name):
    return [item.strip() for item in os.environ.get(name, "").split(",") if item.strip()]


# DEBUG defaults to on for local work; set DEBUG=False in production (Vercel).
DEBUG = os.environ.get("DEBUG", "True").lower() in ("1", "true", "yes", "on")

SECRET_KEY = os.environ.get("SECRET_KEY", "")
if not SECRET_KEY:
    if not DEBUG:
        raise ImproperlyConfigured("Set the SECRET_KEY environment variable when DEBUG is off.")
    SECRET_KEY = "django-insecure-supplyhive-local-development-key"

# ".vercel.app" covers every Vercel deployment; add custom domains with ALLOWED_HOSTS=a.com,b.com
ALLOWED_HOSTS = [".vercel.app", "localhost", "127.0.0.1", *env_list("ALLOWED_HOSTS")]
CSRF_TRUSTED_ORIGINS = ["https://*.vercel.app", *env_list("CSRF_TRUSTED_ORIGINS")]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "shop",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "shop.context_processors.cart_summary",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# DATABASE_URL (e.g. the Neon connection string) wins; without it local SQLite is used.
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        conn_health_checks=True,
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

SESSION_COOKIE_AGE = 60 * 60 * 24 * 14
SESSION_SAVE_EVERY_REQUEST = True

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "Supplyhive <no-reply@supplyhive.local>"

# Payments. With PAYMENT_DEMO_MODE on, a valid UPI/card form counts as a successful payment
# (no money moves). Turn it off until a real payment gateway is wired in shop/payments.py.
PAYMENT_DEMO_MODE = os.environ.get("PAYMENT_DEMO_MODE", "1") == "1"
UPI_MERCHANT_VPA = os.environ.get("UPI_MERCHANT_VPA", "supplyhive@upi")
UPI_MERCHANT_NAME = "Supplyhive"

# GST on stationery (percent). Added on top of the listed price and split into CGST + SGST.
GST_RATE = Decimal(os.environ.get("GST_RATE", "18"))
# Placeholder: replace with the shop's real GSTIN before issuing invoices.
SELLER_GSTIN = os.environ.get("SELLER_GSTIN", "33ABCDE1234F1Z5")

MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

if not DEBUG:
    # Vercel terminates HTTPS and forwards the original scheme in this header.
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
