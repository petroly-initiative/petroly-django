from .base import *

from pathlib import Path
import dj_database_url 
import django_heroku
import os
import cloudinary
from cloudinary import config


SECRET_KEY = os.environ.get("SECRET_KEY", default='')

DEBUG = (os.environ.get("DEBUG", default=True) == 'True')

ALLOWED_HOSTS = ['petroly-main.herokuapp.com']

[
    'maintenance_mode',
] + INSTALLED_APPS

MIDDLEWARE + [
    'maintenance_mode.middleware.MaintenanceModeMiddleware',
]

CONTEXT_PROCESSORS = [
    'maintenance_mode.context_processors.maintenance_mode'
]

MAINTENANCE_MODE = None
MAINTENANCE_MODE_IGNORE_ADMIN_SITE = True
MAINTENANCE_MODE_IGNORE_SUPERUSER = True
MAINTENANCE_MODE_IGNORE_TESTS = True

EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EMAIL_PORT = os.environ.get("EMAIL_PORT")
EMAIL_USE_TLS = (os.environ.get("EMAIL_USE_TLS") == 'True')

# Clouddinary: for media

config(
    cloud_name = os.environ.get("CLOUDINARY_NAME", ''), 
    api_key = os.environ.get("CLOUDINARY_API_KEY", ''), 
    api_secret = os.environ.get("CLOUDINARY_API_SECRET", '') 
)

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(conn_max_age=500)
}


STATIC_URL = '/static/'

MEDIA_URL = '/media/'


django_heroku.settings(locals())
