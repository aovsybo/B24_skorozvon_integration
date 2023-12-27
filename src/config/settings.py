from pathlib import Path
import os
from dotenv import load_dotenv, find_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY"),

YANDEX_DISK_TOKEN = os.environ.get("YANDEX_DISK_TOKEN")
SKOROZVON_LOGIN = os.environ.get("SKOROZVON_LOGIN")
SKOROZVON_API_KEY = os.environ.get("SKOROZVON_API_KEY")
SKOROZVON_APPLICATION_ID = os.environ.get("SKOROZVON_APPLICATION_ID")
SKOROZVON_APPLICATION_KEY = os.environ.get("SKOROZVON_APPLICATION_KEY")

BITRIX_CREATE_DEAL_API_LINK = os.environ.get("BITRIX_CREATE_DEAL_API_LINK")
BITRIX_CREATE_CONTACT_API_LINK = os.environ.get("BITRIX_CREATE_CONTACT_API_LINK")
BITRIX_GET_LIST_OF_CONTACTS = os.environ.get("BITRIX_GET_LIST_OF_CONTACTS")
BITRIX_GET_DEAL_BY_ID = os.environ.get("BITRIX_GET_DEAL_BY_ID")
BITRIX_GET_DEAL_API_URL = os.environ.get("BITRIX_GET_DEAL_API_URL")
BITRIX_GET_DEAL_CATEGORY = os.environ.get("BITRIX_GET_DEAL_CATEGORY")

SCOPES = os.environ.get("SCOPES").split(',')
SAMPLE_SPREADSHEET_ID = os.environ.get("SAMPLE_SPREADSHEET_ID")
TG_API_TOKEN = os.environ.get("TG_API_TOKEN")
TG_ID_RECEIVER = os.environ.get("TG_ID_RECEIVER")
REQUEST_FIELDS = ["TITLE", "CONTACT_ID", "COMMENTS"]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS").split(',')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',

    'integrations',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
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

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME':  os.environ.get("POSTGRES_DB"),
        'USER':  os.environ.get("POSTGRES_USER"),
        'PASSWORD':  os.environ.get("POSTGRES_PASSWORD"),
        'HOST':  os.environ.get("POSTGRES_HOST"),
        'PORT':  os.environ.get("POSTGRES_PORT", 5432),
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
