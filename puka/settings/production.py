from __future__ import annotations

import os  # noqa

from .base import *  # noqa

SECRET_KEY = os.environ["SECRET_KEY"]
DEBUG = False

ALLOWED_HOSTS = ["puka.j3ff.io"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "puka",
        "CONN_MAX_AGE": 600,
        "OPTIONS": {
            "application_name": "puka.j3ff.io",
        },
    },
}

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "console": {
            "format": "%(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "console",
        },
    },
    "loggers": {
        "gunicorn": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": True,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
        "django.security.DisallowedHost": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": True,
        },
    },
}
