# board_project/settings.py
from pathlib import Path
import os
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# ======================================================
# Core settings
# ======================================================

SECRET_KEY = os.environ.get("SECRET_KEY", "demo-secret-key")
DEBUG = os.environ.get("DEBUG", "False") == "True"

# Demo mode switch (used on marketplaces / previews)
DJANGO_DEMO = os.environ.get("DJANGO_DEMO", "").lower() in ("1", "true", "yes")

ALLOWED_HOSTS = os.environ.get(
    "ALLOWED_HOSTS",
    "127.0.0.1,localhost,.onrender.com,.render.com"
).split(",")

# ======================================================
# Installed applications
# ======================================================

INSTALLED_APPS = [
    "board",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.contrib.sites",

    "widget_tweaks",

    # django-allauth
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
]

SITE_ID = 1

# ======================================================
# Middleware
# ======================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",

    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",

    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "board_project.urls"

# ======================================================
# Templates
# ======================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],  # you may add BASE_DIR / "templates"
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",  # required by allauth
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "board.context_processors.menu_categories",
            ],
        },
    },
]

WSGI_APPLICATION = "board_project.wsgi.application"

# ======================================================
# Database
# ======================================================

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
)

DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        ssl_require=True
    )
}

# ======================================================
# Static & Media files
# ======================================================

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static"
] if (BASE_DIR / "static").exists() else []
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ======================================================
# Authentication / django-allauth (NEW API)
# ======================================================

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/accounts/login/"
ACCOUNT_LOGOUT_ON_GET = True

# --- IMPORTANT PART ---
# Login ONLY via email + password
ACCOUNT_LOGIN_METHODS = {"email"}

# Disable passwordless login (email code)
ACCOUNT_LOGIN_BY_CODE_ENABLED = False

# Signup fields (password fields are added automatically)
ACCOUNT_SIGNUP_FIELDS = [
    "first_name",
    "last_name",
    "email",
    
]

# Email verification
ACCOUNT_EMAIL_VERIFICATION = "none" if (DEBUG or DJANGO_DEMO) else "mandatory"

# Custom signup form (optional)
ACCOUNT_FORMS = {
    "signup": "board.forms.AllAuthSignupForm",
}

# ======================================================
# Email configuration
# ======================================================

if DEBUG or DJANGO_DEMO:
    # Console backend for development / demo
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    DEFAULT_FROM_EMAIL = "support@demo.example.com"
else:
    # Production SMTP (example: Gmail)
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
    EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True") == "True"
    EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
    EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
    DEFAULT_FROM_EMAIL = os.environ.get(
        "DEFAULT_FROM_EMAIL",
        "support@yourmarketplace.com"
    )

# ======================================================
# Social authentication (Google)
# ======================================================

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": os.environ.get("GOOGLE_CLIENT_ID", ""),
            "secret": os.environ.get("GOOGLE_CLIENT_SECRET", ""),
            "key": "",
        }
    }
}

# ======================================================
# Logging
# ======================================================

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "loggers": {
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": True,
        },
        "django": {
            "handlers": ["console"],
            "level": "ERROR",
        },
    },
}
# ======================================================
# Security (Render / Production)
# ======================================================

CSRF_TRUSTED_ORIGINS = [
    "https://*.onrender.com",
]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
