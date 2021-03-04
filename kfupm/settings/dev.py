from .base import *

from pathlib import Path
import environ
import cloudinary

env = environ.Env()
env.read_env()

SECRET_KEY = env.str("SECRET_KEY", default='')

DEBUG = env.bool("DEBUG", default=True)

ALLOWED_HOSTS = ["*"]

cloudinary.config(
    cloud_name = env.str("CLOUDINARY_NAME", ''), 
    api_key = env.str("CLOUDINARY_API_KEY", ''), 
    api_secret = env.str("CLOUDINARY_API_SECRET", '') 
)

INTERNAL_IPS = ("127.0.0.1", "172.17.0.1", 'localhost')

# Extra app

INSTALLED_APPS += [
    'debug_toolbar',
]

# Extra middleware

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
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