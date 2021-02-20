"""
Django settings for Puka production deployments.
"""
import django_heroku
from puka.settings.common import *

SECRET_KEY = os.environ["SECRET_KEY"]
DEBUG = False

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

django_heroku.settings(locals(), secret_key=False, databases=False)

# Place static in the same location as webpack build files
STATIC_ROOT = os.path.join(BASE_DIR, "build", "static")
STATICFILES_DIRS = []
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"