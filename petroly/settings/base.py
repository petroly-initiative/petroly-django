from datetime import timedelta
from pathlib import Path
from django.utils.translation import gettext_lazy as _
import os

from gqlauth.settings_type import GqlAuthSettings


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# Application definition
INSTALLED_APPS = [
    'account.apps.AccountConfig',
    'evaluation.apps.EvaluationConfig' ,
    'roommate.apps.RoommateConfig' ,
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cloudinary',
    'django_email_verification',
    'forum',
    'communities',
    'corsheaders',
    'strawberry.django',
    'gqlauth',
    'strawberry_django_jwt.refresh_token',
    'notifier',
    'django_q',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.common.BrokenLinkEmailsMiddleware',
    'account.middleware.AllowOnlyStaffMiddleware',
]

ROOT_URLCONF = 'petroly.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates'
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'petroly.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    # {
    #     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    # },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
]

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'TIMEOUT': 60,
    },
}

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'
# LANGUAGE_CODE = 'ar-SA'

LANGUAGES = [
    ('ar-SA', _('Arabic')),
    ('en-US', _('English')),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale'
]

TIME_ZONE = 'Asia/Riyadh'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]


# MEDIA
MEDIA_ROOT = BASE_DIR / 'media'

LOGIN_REDIRECT_URL = 'index'
LOGIN_URL = 'login'


EMAIL_HOST = 'mail.privateemail.com'
EMAIL_HOST_USER = 'support@petroly.co'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EMAIL_PORT = 465
EMAIL_USE_SSL = True

# Models
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'


AUTHENTICATION_BACKENDS = [
    "gqlauth.backends.GraphQLAuthBackend",
    'django.contrib.auth.backends.ModelBackend',
]



GRAPHQL_JWT = {
    "JWT_VERIFY_EXPIRATION": True,
    "JWT_LONG_RUNNING_REFRESH_TOKEN": True,
    'JWT_EXPIRATION_DELTA': timedelta(minutes=60*24),
    'JWT_REFRESH_EXPIRATION_DELTA': timedelta(days=7),
    # 'JWT_ALLOW_ARGUMENT': True,
    "JWT_ALLOW_ANY_CLASSES": [
        "gqlauth.user.arg_mutations.Register",
        "gqlauth.user.arg_mutations.VerifyAccount",
        "gqlauth.user.arg_mutations.ResendActivationEmail",
        "gqlauth.user.arg_mutations.SendPasswordResetEmail",
        "gqlauth.user.arg_mutations.PasswordReset",
        "gqlauth.user.arg_mutations.ObtainJSONWebToken",
        "gqlauth.user.arg_mutations.VerifyToken",
        "gqlauth.user.arg_mutations.RefreshToken",
        "gqlauth.user.arg_mutations.RevokeToken",
        "gqlauth.user.arg_mutations.VerifySecondaryEmail",
    ],
}



GQL_AUTH = GqlAuthSettings(
    LOGIN_REQUIRED_FIELDS = ['username', 'password'],
    ALLOW_LOGIN_NOT_VERIFIED = False,
    LOGIN_REQUIRE_CAPTCHA = False,
    REGISTER_REQUIRE_CAPTCHA=False,
    ACTIVATION_PATH_ON_EMAIL="confirm",
    EMAIL_TEMPLATE_VARIABLES={
        'frontend_domain': 'petroly.co'
    },
)


Q_CLUSTER = {
    'name': 'petroly',
    'workers': 1,
    'timeout': None,
    'retry': 10,
    'queue_limit': 50,
    'bulk': 10,
    'orm': 'default'
}
