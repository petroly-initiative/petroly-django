from .base import *

from pathlib import Path
import dj_database_url 
import django_heroku
import os
import cloudinary
from cloudinary import config
import re

# Extra app

INSTALLED_APPS += [
    'django.contrib.admindocs',
]

MIDDLEWARE += [
    'account.middleware.DiscordNotificationMiddleware',
]

# For Discord notification
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", default='')


SECRET_KEY = os.environ.get("SECRET_KEY", default='')

DEBUG = (os.environ.get("DEBUG", default=True) == 'True')

ALLOWED_HOSTS = ['.petroly.co', '.petroly-main.herokuapp.com']
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EMAIL_PORT = os.environ.get("EMAIL_PORT")
EMAIL_USE_SSL = (os.environ.get("EMAIL_USE_SSL") == 'True')

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

# To get Email when >500 error happens
SERVER_EMAIL = 'Error@petroly.co'
ADMINS = [
    ('Ammar', 'A@ammarf.com')
]
# To get 404 errors
MANAGERS = ADMINS
# Ignore these pattern errors
IGNORABLE_404_URLS = [
    re.compile(r'^/apple-touch-icon.*\.png$'),
    re.compile(r'^/favicon\.ico$'),
    re.compile(r'^/robots\.txt$'),
]

django_heroku.settings(locals())
