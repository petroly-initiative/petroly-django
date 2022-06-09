from .base import *
from corsheaders.defaults import default_headers

from pathlib import Path
import environ
import cloudinary

env = environ.Env()
env.read_env()

SECRET_KEY = env.str("SECRET_KEY", default='')

DEBUG = True

ALLOWED_HOSTS = ["*"]

EMAIL_HOST = 'mail.privateemail.com'
EMAIL_HOST_USER = 'support@petroly.co'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD", "")
EMAIL_PORT = 465
EMAIL_USE_SSL = True


cloudinary.config(
    cloud_name = 'petroly-initiative',
    api_key = '777263134962661',
    api_secret = env.str("CLOUDINARY_API_SECRET", '') 
)

INTERNAL_IPS = ("127.0.0.1", "172.17.0.1", 'localhost')

# Extra app

INSTALLED_APPS += [
    'debug_toolbar',
    'django.contrib.admindocs',
]

# Extra middleware

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
] + MIDDLEWARE


CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_HEADERS = list(default_headers) + [
    'Accept-Language'
]

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


STATIC_URL = '/static/'

MEDIA_URL = '/media/'