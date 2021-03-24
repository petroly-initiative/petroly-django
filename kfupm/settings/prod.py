from .base import *

from pathlib import Path
import dj_database_url 
import django_heroku
import environ
import os
import cloudinary
from cloudinary import config

env = environ.Env()
env.read_env()

SECRET_KEY = os.environ.get("SECRET_KEY", default='')

DEBUG = os.environ.get("DEBUG", default=True)

ALLOWED_HOSTS = ['petroly-main.herokuapp.com']

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