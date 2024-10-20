from pathlib import Path
import os
from decouple import config, Csv
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# WKHTMLTOPDF_PATH = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    

WKHTMLTOPDF_PATH = config("WKHTMLTOPDF_PATH")

SECRET_KEY = config("SECRET_KEY")


# DEBUG = config('DEBUG', cast=bool)
DEBUG = True

ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv())


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "cenartechapp",
    "active_link",
    'wkhtmltopdf',
]

CSRF_TRUSTED_ORIGINS = [
    'https://cenartechmanagement.top',
    'http://cenartechmanagement.top',
]

# Increase POST data limit
DATA_UPLOAD_MAX_MEMORY_SIZE = 1048576

# Increase file upload size limit
FILE_UPLOAD_MAX_MEMORY_SIZE = 1048576


SECURE_SSL_REDIRECT = True
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')



MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'cenartechapp.middleware.Custom404Middleware',
    # 'cenartechapp.middleware.Custom403Middleware',
    # 'cenartechapp.middleware.Custom500Middleware',
    'whitenoise.middleware.WhiteNoiseMiddleware'
]

ROOT_URLCONF = 'cenartechpro.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR /'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cenartechapp.context_processors.current_year',
                'cenartechapp.context_processors.school_info',
                
            ],
        },
    },
]

WSGI_APPLICATION = 'cenartechpro.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases



DATABASES = {
    'default': {
        'ENGINE': config("ENGINE"),
        'NAME': config("NAME"),
        'USER': config("USER"),
        'PASSWORD': config("PASSWORD"),
        'HOST': config("HOST"),
        'PORT': config("PORT"),
    }
}

# if not DEBUG and config('DBURL') is not None:
# DATABASES['default'] = dj_database_url.parse(config('DBURL'))


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = os.path.join(BASE_DIR, 'static'),

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'





MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = config('AUTH_USER_MODEL') 


MAIL_BACKEND = config('EMAIL_BACKEND')
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT')
EMAIL_USE_TLS = config('EMAIL_USE_TLS')
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')

SCHOOL_NAME = config('SCHOOL_NAMES')
SCHOOL_SLOGAN = config('SCHOOL_SLOGANS')
SCHOOL_LOCATION = config('SCHOOL_LOCATIONS')
SCHOOL_NUM = config('SCHOOL_NUMS')
SCHOOL_WEB = config('SCHOOL_WEBS')
SCHOOL_MARKS = config('SCHOOL_MARKSS')
