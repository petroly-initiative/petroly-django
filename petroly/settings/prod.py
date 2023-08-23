import os
import re

import dj_database_url
import cloudinary
from django.test.runner import DiscoverRunner

from .base import *

IS_HEROKU = "DYNO" in os.environ


# Generally avoid wildcards(*). However since Heroku router provides hostname validation it is ok
SECRET_KEY = os.environ.get("SECRET_KEY")
DEBUG = os.environ.get("DEBUG", "False") == "True"

if IS_HEROKU:
    ALLOWED_HOSTS = ["*"]
else:
    ALLOWED_HOSTS = []

# Extra app
INSTALLED_APPS += [
    "django.contrib.admindocs",
]

MIDDLEWARE += [
    "account.middleware.DiscordNotificationMiddleware",
]

# For Discord notification
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", default="")


ALLOWED_HOSTS = [
    ".petroly.co",
    ".petroly-main.herokuapp.com",
    "petroly-pr-201.herokuapp.com",
]
# get other hosts from env
hosts = os.environ.get("ALLOWED_HOSTS", "")
if hosts:
    for host in hosts.split(","):
        ALLOWED_HOSTS.append(host)


SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# CORS lib
CORS_ALLOWED_ORIGINS = [
    "https://petroly.vercel.app",
    "https://react.petroly.co",
    "https://petroly.co",
]


# Clouddinary: for media
cloudinary.config(
    cloud_name="petroly-initiative",
    api_key="777263134962661",
    api_secret=os.environ.get("CLOUDINARY_API_SECRET", ""),
)

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
# Check if DATABASE_URL is provided
# otherwise fallback to basic db
MAX_CONN_AGE = 600

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

if "DATABASE_URL" in os.environ:
    # Configure Django for DATABASE_URL environment variable.
    DATABASES["default"] = dj_database_url.config(
        conn_max_age=MAX_CONN_AGE, ssl_require=True
    )

    # Enable test database if found in CI environment.
    if "CI" in os.environ:
        DATABASES["default"]["TEST"] = DATABASES["default"]


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/
MEDIA_URL = "/media/"
STATIC_URL = "/static/"

# Enable WhiteNoise's GZip compression of static assets.
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# Test Runner Config
class HerokuDiscoverRunner(DiscoverRunner):
    """Test Runner for Heroku CI, which provides a database for you.
    This requires you to set the TEST database (done for you by settings().)"""

    def setup_databases(self, **kwargs):
        self.keepdb = True
        return super(HerokuDiscoverRunner, self).setup_databases(**kwargs)


# Use HerokuDiscoverRunner on Heroku CI
if "CI" in os.environ:
    TEST_RUNNER = "gettingstarted.settings.HerokuDiscoverRunner"


# To get Email when >500 error happens
SERVER_EMAIL = "Error@petroly.co"
ADMINS = [("Ammar", "me@ammarf.sa")]
# To get 404 errors
MANAGERS = ADMINS
# Ignore these pattern errors
IGNORABLE_404_URLS = [
    re.compile(r"^/apple-touch-icon.*\.png$"),
    re.compile(r"^/favicon\.ico$"),
    re.compile(r"^/robots\.txt$"),
    re.compile(r"^/ads\.txt$"),
]
