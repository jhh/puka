from __future__ import annotations

from .base import *  # noqa: F403

SECRET_KEY = "django-insecure-usp0sg081f=9+_j95j@-k^sfp+9c*!qrwh-m17%=_9^xot#9fn"

# ``admin_client`` creates a superuser per test; PBKDF2 costs ~155 ms each.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

STATIC_ROOT = ""
