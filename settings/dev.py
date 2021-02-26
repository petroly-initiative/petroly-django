from .base import *

from pathlib import Path
import environ
import cloudinary

env = environ.Env()
env.read_env()

SECRET_KEY = env.str("SECRET_KEY", default='')

DEBUG = env.bool("DEBUG", default=True)

ALLOWED_HOSTS = ["localhost"]

cloudinary.config(
    cloud_name = env.str("CLOUDINARY_NAME", ''), 
    api_key = env.str("CLOUDINARY_API_KEY", ''), 
    api_secret = env.str("CLOUDINARY_API_SECRET", '') 
)

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