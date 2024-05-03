from datetime import timedelta
import os
from pathlib import Path
import re

import dj_database_url
from django.utils.translation import gettext_lazy as _
import environ
from gqlauth.settings_type import GqlAuthSettings

from petroly.log import CUSTOM_LOGGING

LOGGING = CUSTOM_LOGGING

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False),
    FLY_APP_NAME=(str, ""),
)
env.read_env(overwrite=False)

SECRET_KEY = env("SECRET_KEY")

# False if not in os.environ because of casting above
DEBUG = env("DEBUG")

APP_NAME = env("FLY_APP_NAME")

if APP_NAME:
    ALLOWED_HOSTS = [f"{APP_NAME}.fly.dev", ".ammarf.sa"]
    SECURE_SSL_REDIRECT = True
    # django server lives behind Fly.io proxy to connect to django server
    # forcing HTTPS  to prevent infinite redirects we need to set following:
    # X-Forwarded-Proto	Original client protocol, either http or https
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # CORS lib
    CORS_ALLOWED_ORIGINS = [
        "https://petroly.vercel.app",
        "https://react.petroly.co",
        "https://petroly.co",
    ]
else:
    DEBUG = True
    ALLOWED_HOSTS = ["*"]


# Application definition
INSTALLED_APPS = [
    "django.contrib.admindocs",
    "account.apps.AccountConfig",
    "evaluation.apps.EvaluationConfig",
    "roommate.apps.RoommateConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "cloudinary",
    "django_email_verification",
    "forum",
    "communities",
    "corsheaders",
    "strawberry.django",
    "gqlauth",
    "notifier",
    "django_q",
    "telegram_bot",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "gqlauth.core.middlewares.django_jwt_middleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.common.BrokenLinkEmailsMiddleware",
    "account.middleware.AllowOnlyStaffMiddleware",
    "account.middleware.DiscordNotificationMiddleware",
]

ROOT_URLCONF = "petroly.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "petroly.wsgi.application"


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    # {
    #     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    # },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
]


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
    DATABASES["default"] = dj_database_url.config(conn_max_age=MAX_CONN_AGE)


# Models
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Cache
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "TIMEOUT": 40,
    },
}

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/
LANGUAGE_CODE = "en-us"
# LANGUAGE_CODE = 'ar-SA'

LANGUAGES = [
    ("ar-SA", _("Arabic")),
    ("en-US", _("English")),
]

LOCALE_PATHS = [BASE_DIR / "locale"]
TIME_ZONE = "Asia/Riyadh"
USE_I18N = True
USE_L10N = False
USE_TZ = True
DATETIME_FORMAT = "N j, Y, H:i:s"


# Static files (CSS, JavaScript, Images)
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]


# MEDIA
MEDIA_ROOT = BASE_DIR / "media"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/
MEDIA_URL = "/media/"
STATIC_URL = "/static/"

# Enable WhiteNoise's GZip compression of static assets.
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

LOGIN_REDIRECT_URL = "index"
LOGIN_URL = "login"


EMAIL_HOST = "mail.privateemail.com"
EMAIL_HOST_USER = "support@petroly.co"
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EMAIL_PORT = 465
EMAIL_USE_SSL = True

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

# For Discord notification
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", default="")

# Telegram
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

GQL_AUTH = GqlAuthSettings(
    ALLOW_LOGIN_NOT_VERIFIED=False,
    LOGIN_REQUIRE_CAPTCHA=False,
    REGISTER_REQUIRE_CAPTCHA=False,
    JWT_LONG_RUNNING_REFRESH_TOKEN=True,
    ACTIVATION_PATH_ON_EMAIL="confirm",
    EMAIL_TEMPLATE_VARIABLES={"frontend_domain": "petroly.co"},
    JWT_REFRESH_EXPIRATION_DELTA=timedelta(days=30),
    JWT_EXPIRATION_DELTA=timedelta(days=1),
)

STRAWBERRY_DJANGO = {
    "FIELD_DESCRIPTION_FROM_HELP_TEXT": True,
    "TYPE_DESCRIPTION_FROM_MODEL_DOCSTRING": True,
    "MUTATIONS_DEFAULT_HANDLE_ERRORS": True,
    "GENERATE_ENUMS_FROM_CHOICES": True,
    "MAP_AUTO_ID_AS_GLOBAL_ID": True,
}

Q_CLUSTER = {
    "name": "petroly",
    "workers": int(os.environ.get("Q_CLUSTER_WORKERS", 1)),
    "timeout": 60 * 2,
    "retry": 60 * 60 * 24,  # 1 day
    "queue_limit": 50,
    "bulk": 10,
    "orm": "default",
    "save_limit": 10_000,
    "max_attempts": 2,
}
