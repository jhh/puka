from __future__ import annotations

import os
from pathlib import Path

import environs

BASE_DIR = Path(__file__).resolve().parent.parent.parent
APPS_DIR = BASE_DIR / "puka"

env = environs.Env()

ALLOWED_HOSTS: list[str] = []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_htmx",
    "template_partials",
    "django_filters",
    "crispy_forms",
    "crispy_tailwind",
    "taggit",
    "treebeard",
    "puka.bookmarks",
    "puka.core",
    "puka.stuff",
    "puka.upkeep",
    "puka.users",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.auth.middleware.LoginRequiredMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "puka.urls"

# Database configuration
# DJANGO_DATABASE_URL e.g. postgres:///${REPO_NAME}?pool=true
DATABASES = {
    "default": (
        env.dj_db_url(
            "DJANGO_DATABASE_URL",
            default="postgres:///puka",
        )
    ),
}

# DJANGO_DATABASE_OPTIONS e.g. '{"pool": {"min_size": 2, "max_size": 4}}'
if env.str("DJANGO_DATABASE_OPTIONS", ""):
    DATABASES["default"]["OPTIONS"] = DATABASES["default"].get("OPTIONS", {}) | env.json("DJANGO_DATABASE_OPTIONS")  # fmt: off

# Custom User Model
AUTH_USER_MODEL = "users.CustomUser"

# Template configuration

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(APPS_DIR / "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "puka.core.context_processors.htmx",
            ],
        },
    },
]

WSGI_APPLICATION = "puka.wsgi.application"

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"

# STATIC_ROOT is where collectstatic will collect files for deployment
STATIC_ROOT = os.environ.get("DJANGO_STATIC_ROOT", BASE_DIR / "static")

# STATICFILES_DIR is where "django.contrib.staticfiles" looks during development
STATICFILES_DIRS = [str(APPS_DIR / "static")]

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_REDIRECT_URL = "/"

TAGGIT_CASE_INSENSITIVE = True

CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACK = "tailwind"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "localhost"
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False

ADMINS = [("Jeff", "jeff@j3ff.io")]
