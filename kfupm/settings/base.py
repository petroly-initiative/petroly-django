from datetime import timedelta
from pathlib import Path
from django.utils.translation import gettext_lazy as _


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# Application definition
INSTALLED_APPS = [
    'maintenance_mode',
    'account.apps.AccountConfig',
    'evaluation.apps.EvaluationConfig' ,
    'roommate.apps.RoommateConfig' ,
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_filters',
    'bootstrapform',
    'widget_tweaks',
    'cloudinary',
    'django_email_verification',
    'graphene_django',
    'graphql_jwt.refresh_token.apps.RefreshTokenConfig',
    'graphql_auth',
    'mathfilters',
    'forum',
    'whatsapp',
    'corsheaders',
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
    'maintenance_mode.middleware.MaintenanceModeMiddleware',
]

ROOT_URLCONF = 'kfupm.urls'

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
                'maintenance_mode.context_processors.maintenance_mode',
            ],
        },
    },
]

WSGI_APPLICATION = 'kfupm.wsgi.application'


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

CONTEXT_PROCESSORS = [
    'maintenance_mode.context_processors.maintenance_mode'
]

MAINTENANCE_MODE = None
MAINTENANCE_MODE_IGNORE_ADMIN_SITE = True
MAINTENANCE_MODE_IGNORE_SUPERUSER = True
MAINTENANCE_MODE_IGNORE_TESTS = True

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

# LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'ar-SA'

LANGUAGES = [
    ('ar', _('Arabic')),
    ('en', _('English')),
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



# Email verification
def verified_callback(user):
    user.status.verified = True
    user.status.save()


EMAIL_VERIFIED_CALLBACK = verified_callback
EMAIL_FROM_ADDRESS = 'support@petroly.co'
EMAIL_MAIL_SUBJECT = 'Confirm Your Email'
EMAIL_MAIL_HTML = 'email_body.html'
EMAIL_MAIL_PLAIN = 'email_body.txt'
EMAIL_PAGE_TEMPLATE = 'email_done.html'
EMAIL_PAGE_DOMAIN = 'https://www.petroly.co/'
EMAIL_TOKEN_LIFE = 60 * 60 * 5


# Models
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'


AUTHENTICATION_BACKENDS = [
    # 'graphql_jwt.backends.JSONWebTokenBackend',
    'graphql_auth.backends.GraphQLAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# GraphQL
GRAPHENE = {
    'SCHEMA': 'kfupm.schema.schema',
    'MIDDLEWARE': [
        'graphql_jwt.middleware.JSONWebTokenMiddleware',
    ],
}

GRAPHQL_JWT = {
    "JWT_VERIFY_EXPIRATION": True,
    "JWT_LONG_RUNNING_REFRESH_TOKEN": True,
    'JWT_EXPIRATION_DELTA': timedelta(minutes=60*24),
    'JWT_REFRESH_EXPIRATION_DELTA': timedelta(days=7),
    # 'JWT_ALLOW_ARGUMENT': True,
    "JWT_ALLOW_ANY_CLASSES": [
        "graphql_auth.mutations.Register",
        "graphql_auth.mutations.VerifyAccount",
        "graphql_auth.mutations.ResendActivationEmail",
        "graphql_auth.mutations.SendPasswordResetEmail",
        "graphql_auth.mutations.PasswordReset",
        "graphql_auth.mutations.ObtainJSONWebToken",
        "graphql_auth.mutations.VerifyToken",
        "graphql_auth.mutations.RefreshToken",
        "graphql_auth.mutations.RevokeToken",
        "graphql_auth.mutations.VerifySecondaryEmail",
    ],
}

GRAPHQL_AUTH = {
    "ACTIVATION_PATH_ON_EMAIL": "account/activate",
    "EMAIL_TEMPLATE_ACTIVATION": "activation_email.html",
    "EMAIL_TEMPLATE_ACTIVATION_RESEND": "activation_email.html",
    "EMAIL_TEMPLATE_SECONDARY_EMAIL_ACTIVATION": "email/activation_email.html",
    "EMAIL_TEMPLATE_PASSWORD_SET": "email/password_set_email.html",
    "EMAIL_TEMPLATE_PASSWORD_RESET": "email/password_reset_email.html",
}