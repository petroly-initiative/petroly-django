from .base import *

from pathlib import Path
import dj_database_url 
import django_heroku
import environ

env = environ.Env()
env.read_env()

SECRET_KEY = env.str("SECRET_KEY", default='')

DEBUG = env.bool("DEBUG", default=True)

ALLOWED_HOSTS = ['ccwebsite1.herokuapp.com']


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(conn_max_age=500)
}


STATIC_URL = '/static/'

MEDIA_URL = '/media/'


django_heroku.settings(locals())