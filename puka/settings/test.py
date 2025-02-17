from __future__ import annotations

import os
from warnings import filterwarnings

from .base import *  # noqa: F403

SECRET_KEY = "django-insecure-usp0sg081f=9+_j95j@-k^sfp+9c*!qrwh-m17%=_9^xot#9fn"

# Django 6 deprecation warning
filterwarnings("ignore", "The FORMS_URLFIELD_ASSUME_HTTPS transitional setting is deprecated.")
FORMS_URLFIELD_ASSUME_HTTPS = True

STATIC_ROOT = ""

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "USER": os.getenv("PGUSER", "postgres"),
        "HOST": os.getenv("PGHOST", "127.0.0.1"),
        "TEST": {
            "NAME": os.getenv("PGDATABASE", "test_puka"),
        },
    },
}
