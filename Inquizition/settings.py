"""
Django settings for Inquizition project.

Generated by 'django-admin startproject' using Django 2.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
from django.contrib.messages import constants as messages

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'jz&io2&7r9!de@a36p(tvjvn5jxqtfm7o0m2a&^jn3b__!x8$t'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users.apps.UsersConfig',
    'courses.apps.CoursesConfig',
    'flashcard.apps.FlashcardConfig',
    'construct.apps.ConstructConfig',
    'bootstrapform',
    'django_extensions',
    'storages',
    'review.apps.ReviewConfig',
    'debug_toolbar',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',

]

ROOT_URLCONF = 'Inquizition.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'Inquizition.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/
# Django - Bootstrap message tags
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}


#STATIC_URL = '/static/'
#STATICFILES_DIRS = (os.path.join(BASE_DIR,'static'),)

AUTH_USER_MODEL = 'users.CustomUser'

LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'
LOGIN_URL = '/users/login'


AWS_ACCESS_KEY_ID = 'AKIAVUKRNCJBSKGWLHUW'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'inquizition-static'

AWS_S3_CUSTOM_DOMAIN = 'dqktggxxlj4o5.cloudfront.net'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_LOCATION = 'static'


STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

#d3fjutrnryyv0e.cloudfront.net

MEDIA_ROOT=os.path.join(BASE_DIR,"media")
MEDIA_URL='/media/'

# INTERNAL_IPS = [
#      '127.0.0.1',
#  ]

DEBUG_TOOLBAR_PATCH_SETTINGS = False

def get_cache():
  import os
  try:
    servers = os.environ['MEMCACHIER_SERVERS']
    username = os.environ['MEMCACHIER_USERNAME']
    password = os.environ['MEMCACHIER_PASSWORD']
    return {
      'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
        # TIMEOUT is not the connection timeout! It's the default expiration
        # timeout that should be applied to keys! Setting it to `None`
        # disables expiration.
        'TIMEOUT': None,
        'LOCATION': servers,
        'OPTIONS': {
          'binary': True,
          'username': username,
          'password': password,
          'behaviors': {
            # Enable faster IO
            'no_block': True,
            'tcp_nodelay': True,
            # # Keep connection alive
            # 'tcp_keepalive': True,
            # # Timeout settings
            # 'connect_timeout': 2000, # ms
            # 'send_timeout': 750 * 1000, # us
            # 'receive_timeout': 750 * 1000, # us
            # '_poll_timeout': 2000, # ms
            # # Better failover
            # 'ketama': True,
            # 'remove_failed': 1,
            # 'retry_timeout': 2,
            # 'dead_timeout': 30,
          }
        }
      }
    }
  except:
    return {
      'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
      }
    }

CACHES = get_cache()
import os
CACHES = {
        "default": {
            "BACKEND": 'django.core.cache.backends.memcached.PyLibMCCache',
            "LOCATION": os.environ['MEMCACHIER_SERVERS'],
            "OPTIONS": {
            
        }
    },
    'dummy': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        'LOCATION': 'unique-snowflake',
    }
}

SESSION_ENGINE= "django.contrib.sessions.backends.cached_db"
