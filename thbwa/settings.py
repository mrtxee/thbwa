from pathlib import Path
import os
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-=z^o$spdg7a6$p!smi9vv49s9_0^3*ko%y(uu#2*6h1uf%*j!m'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
#CORS_ORIGIN_ALLOW_ALL = DEBUG
ALLOWED_HOSTS = ['*']

# CSRF_COOKIE_NAME = "XSRF-TOKEN"
# CSRF_COOKIE_NAME = "csrftoken"

# Application definition
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = 'admin@tuyahome.online'
SERVER_EMAIL = "admin@tuyahome.online"
DEFAULT_FROM_EMAIL = "admin@tuyahome.online"
EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'django_bootstrap5',
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',

    'main',
    'backend',
]

REST_FRAMEWORK = {
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    # 'PAGE_SIZE': 10,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ]
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware'
]

ROOT_URLCONF = 'thbwa.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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
AUTHENTICATION_BACKENDS = [
    # ...
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
    # ...
]
WSGI_APPLICATION = 'thbwa.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

#STATIC_URL = 'static/'
#STATIC_ROOT = BASE_DIR / 'static'

if DEBUG:
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, 'core/static/'),
    ]
    STATIC_URL = 'static/'
    STATIC_ROOT = os.path.join(BASE_DIR, "static/")

    MEDIA_URL = '/media/'  
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

else:
    MEDIA_ROOT = '/var/www/thbwa/media'
    MEDIA_URL = '/media/'
    STATIC_ROOT = '/var/www/thbwa/static'
    STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# django-allauth config in here

SITE_ID = 1
LOGIN_REDIRECT_URL = '/devices/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/#HP'
ACCOUNT_SIGNUP_REDIRECT_URL = '/user/profile/'
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_USERNAME_MIN_LENGTH = 5
SOCIALACCOUNT_LOGIN_ON_GET = True
ACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = "none"
REST_USE_JWT = True

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
            'openid',
            # 'https://www.googleapis.com/auth/calendar.readonly'
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'APP': {
            #            'client_id': 'xxx-pron',
            #            'secret': 'xxx-pron',
        }

    }
}
