from __future__ import annotations

import os

import environs

from .base import *  # noqa: F403

env = environs.Env()

SECRET_KEY = os.environ["SECRET_KEY"]
DEBUG = False

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["puka.j3ff.io"])

if env.path("DJANGO_STATICFILES_DIR", None):
    STATICFILES_DIRS.append(str(env.path("DJANGO_STATICFILES_DIR")))  # noqa: F405

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

EMAIL_PORT = 25

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
