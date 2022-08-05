import warnings
from .base import *
from .constants import COSTOM_LOGGING


from pathlib import Path
import dj_database_url 
import django_heroku
import cloudinary
import os
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


SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = os.environ.get("DEBUG", 'False') == 'True'

ALLOWED_HOSTS = ['.petroly.co', '.petroly-main.herokuapp.com']
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

CORS_ALLOWED_ORIGINS = ['https://petroly.vercel.app', 'https://react.petroly.co', 'https://petroly.co']


# Clouddinary: for media
cloudinary.config(
    cloud_name = 'petroly-initiative',
    api_key = '777263134962661',
    api_secret = os.environ.get("CLOUDINARY_API_SECRET", '') 
)

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
# Check if DATABASE_URL is provided
# otherwise fallback to basic db
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
    re.compile(r'^/ads\.txt$'),
]


django_heroku.settings(locals())
