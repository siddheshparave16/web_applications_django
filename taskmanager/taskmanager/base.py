"""
Django settings for taskmanager project.

Generated by 'django-admin startproject' using Django 5.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-=m@9kt-z@8wvqo8a#8d#x4-rjw)!kw=s*9*9_$5*ocln9q1tw)"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # manually installed apps
    "django_extensions",
    "tasks",
    "storages",
    "widget_tweaks",
    "accounts",
    "health",
]

MIDDLEWARE = [
    "tasks.middlewares.RequestTimeMiddleware",  # Custom middleware
    "django.middleware.security.SecurityMiddleware",
    "csp.middleware.CSPMiddleware",  # CSP Middleware (Add it here)
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "taskmanager.urls"

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
                "tasks.context_processors.feature_flags",
            ],
        },
    },
]


# Custom Settings
TEMPLATE_PARTS = {
    "header": "tasks/_header.html",
    "footer": "tasks/_footer.html",
}


WSGI_APPLICATION = "taskmanager.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",  # From ConfigMap
        "NAME": os.getenv("DB_NAME"),   # From ConfigMap
        "USER": os.getenv("DB_USER"),   # From ConfigMap
        "PASSWORD": os.getenv("DB_PASSWORD"),  # From Secret
        "HOST": os.getenv("DB_HOST"),   # From ConfigMap
        "PORT": os.getenv("DB_PORT"),   # From ConfigMap
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "/static/"

STATIC_ROOT = os.path.join(
    BASE_DIR, "staticfiles"
)  # For `collectstatic` command in production

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "tasks/static"),  # Correct path to the static directory
]


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

INTERNAL_IPS = [
    "127.0.0.1",  # Add your local IP here
]

# new storage
# STORAGES = {"staticfiles": {"BACKEND": "storages.backends.s3boto3.S3StaticStorage"}}

# AWS_S3_ACCESS_KEY_ID = os.getenv("AWS_S3_ACCESS_KEY_ID")
# AWS_S3_SECRET_ACCESS_KEY = os.getenv("AWS_S3_SECRET_ACCESS_KEY")


# Email settings configuration - Custom settings
# - In DEBUG mode, emails are printed to the console for development/testing.
# - In production (DEBUG=False), emails are sent using SMTP.
# - Environment variables are used for production settings with default fallbacks.
# - EMAIL_USE_TLS must be set to "True" as a string for TLS to be enabled.


if DEBUG:
    EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
    EMAIL_HOST = os.getenv("EMAIL_HOST", "localhost")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", 1025))
    EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "False").lower() == "true"

else:
    EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
    EMAIL_HOST = os.getenv("EMAIL_HOST", "localhost")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", 1025))
    EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "False").lower() == "true"



# Media files
MEDIA_ROOT = os.path.join(BASE_DIR, "media/")
MEDIA_URL = "/media/"

# SESSION_ENGINE = "django.contrib.sessions.backends.db"  # Default (not Redis)



# login and logout redirect

LOGIN_REDIRECT_URL = "tasks:home"
LOGOUT_REDIRECT_URL = "accounts:login"


# configuration for project to use new user model
AUTH_USER_MODEL = "accounts.TaskManagerUser"

AUTHENTICATION_BACKEND = [
    "accounts.backends.OrganizationUsernameOrEmailBackend",
]


# # In development, keep it False unless you are testing with HTTPS.
# SESSION_COOKIE_SECURE = False
# CSRF_COOKIE_SECURE = False


# Content Security Policy (CSP) Settings
CSP_DEFAULT_SRC = ("'self'",)  # Allow content only from our own domain

CSP_STYLE_SRC = (
    "'self'",
    "https://cdn.jsdelivr.net",
    "https://code.jquery.com",
    "'unsafe-inline'",
)  # Allow external styles

CSP_SCRIPT_SRC = (
    "'self'",
    "https://cdn.jsdelivr.net",
    "https://code.jquery.com",
    "'unsafe-inline'",
)  # Allow external scripts

CSP_IMG_SRC = (
    "'self'",
    "data:",
    "https://your-cdn.com",
    "https://example.com",
)  # Allow images from our domain & external sources


# Prevents browsers from MIME-type sniffing, enforcing declared Content-Type
SECURE_CONTENT_TYPE_NOSNIFF = True


# Ensures browsers only send the Referer header to the same origin, improving privacy
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"


# Use Argon2 for stronger security, with PBKDF2 as a fallback.
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",  # Default
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",  # Fallback
]


# URL for admin
ADMIN_URL = "tm-admin-portal/"


# Default number of items per page for paginated API responses.
# This value applies globally to all endpoints unless overridden by a custom pagination class.
# NINJA_PAGINATION_PER_PAGE = 5

NINJA_PAGINATION_CLASS = "tasks.pagination.CustomTaskManagerPagination"

JWT_SECRET_KEY = os.getenv("JWT_SECRETE_KEY", "jwt_secret")
JWT_REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY", "jwt_refresh_secret")

# Disable Redis for local development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}