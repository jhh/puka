"""
Django settings for Puka development.
"""
from puka.settings.common import *

SECRET_KEY = "gy=mqm_f*98ghz2zq$*uq%v1!!n!!b0u995$)=7-4q!!*3tt-q"
DEBUG = True

ALLOWED_HOSTS = []

os.environ.setdefault("DATABASE_URL", "postgres://127.0.0.1:5432/puka")
DATABASES = {"default": dj_database_url.config()}
