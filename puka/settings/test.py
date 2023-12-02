from __future__ import annotations

from .base import *  # noqa

SECRET_KEY = "django-insecure-usp0sg081f=9+_j95j@-k^sfp+9c*!qrwh-m17%=_9^xot#9fn"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "puka-test",
        "USER": "jeff",
        "PASSWORD": "",
        "HOST": "127.0.0.1",
        "PORT": "5432",
    },
}

TAILWIND_CSS = "css/main.css"
