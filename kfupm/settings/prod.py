from .base import *

from pathlib import Path
import dj_database_url 
import django_heroku
import environ
import os
import cloudinary

env = environ.Env()
env.read_env()

SECRET_KEY = os.environ.get("SECRET_KEY", default='')

DEBUG = env.bool("DEBUG", default=True)
DEBUG = os.environ.get("DEBUG", default=True)

ALLOWED_HOSTS = ['ccwebsite1.herokuapp.com']

# Clouddinary: for media

cloudinary.config(
    cloud_name = env.str("CLOUDINARY_NAME", ''), 
    api_key = env.str("CLOUDINARY_API_KEY", ''), 
    api_secret = env.str("CLOUDINARY_API_SECRET", '') 
)

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(conn_max_age=500)
}


STATIC_URL = '/static/'

MEDIA_URL = '/media/'


django_heroku.settings(locals())