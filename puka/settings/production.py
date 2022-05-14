"""
Django settings for Puka production deployments.
"""
from puka.settings.common import *

SECRET_KEY = os.environ["SECRET_KEY"]
DEBUG = False

SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0

ALLOWED_HOSTS = ["*"]

DATABASES = {"default": dj_database_url.config(conn_max_age=600, ssl_require=False)}

STATIC_ROOT = os.path.join(BASE_DIR, "build", "static")
STATICFILES_DIRS = []
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": (
                "%(asctime)s [%(process)d] [%(levelname)s] "
                + "pathname=%(pathname)s lineno=%(lineno)s "
                + "funcname=%(funcName)s %(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "handlers": {
        "null": {
            "level": "DEBUG",
            "class": "logging.NullHandler",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "testlogger": {
            "handlers": ["console"],
            "level": "INFO",
        }
    },
}
