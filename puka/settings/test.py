from __future__ import annotations

from warnings import filterwarnings

from .base import *  # noqa: F403

SECRET_KEY = "django-insecure-usp0sg081f=9+_j95j@-k^sfp+9c*!qrwh-m17%=_9^xot#9fn"

# ``admin_client`` creates a superuser per test; PBKDF2 costs ~155 ms each.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Django 6 deprecation warning
filterwarnings("ignore", "The FORMS_URLFIELD_ASSUME_HTTPS transitional setting is deprecated.")
FORMS_URLFIELD_ASSUME_HTTPS = True

STATIC_ROOT = ""
