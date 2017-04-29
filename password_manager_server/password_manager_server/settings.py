"""
Django settings for password_manager_server project.

Generated by 'django-admin startproject' using Django 1.8.3.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import yaml
import json
import hashlib
HOME = os.path.expanduser('~')

with open(os.path.join(HOME, '.psono_server', 'settings.yaml'), 'r') as stream:
    config = yaml.load(stream)




def config_get(key, *args):
    if 'PSONO_' + key in os.environ:
        val = os.environ.get('PSONO_' + key)
        try:
            json_object = json.loads(val)
        except ValueError:
            return val
        return json_object
    if key in config:
        return config.get(key)
    if len(args) > 0:
        return args[0]
    raise Exception("Setting missing", "Couldn't find the setting for %s (maybe you forget the 'PSONO_' prefix in the environment variable" % (key,))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config_get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config_get('DEBUG')

ALLOWED_HOSTS = config_get('ALLOWED_HOSTS')
ALLOWED_DOMAINS = config_get('ALLOWED_DOMAINS')

HOST_URL = config_get('HOST_URL')

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'corsheaders',
    'rest_framework',
    'restapi',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'middleware.sqlprinter.SQLLogToConsoleMiddleware',
)

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
)

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAdminUser',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'restapi.parsers.DecryptJSONParser',
        # 'rest_framework.parsers.FormParser', # default for Form Parsing
        'rest_framework.parsers.MultiPartParser' # default for UnitTest Parsing
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'restapi.renderers.EncryptJSONRenderer',
        # 'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.ScopedRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '1440/day',
        'user': '28800/day',
        'health_check': '60/hour',
        'ga_verify': '10/minute',
        'yubikey_otp_verify': '10/minute',
        'registration': '6/day',
    },
    'PAGE_SIZE': 10
}


for key, value in config_get('DEFAULT_THROTTLE_RATES', {}).items():
    REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'][key] = value


ROOT_URLCONF = 'password_manager_server.urls'
SITE_ID = 1

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = (
        'GET',
        'POST',
        'PUT',
        'PATCH',
        'DELETE',
        'OPTIONS'
    )
CORS_ALLOW_HEADERS = (
        'x-requested-with',
        'content-type',
        'accept',
        'origin',
        'authorization',
        'x-csrftoken',
        'accept-encoding'
    )

TEMPLATES = config_get('TEMPLATES')

WSGI_APPLICATION = 'password_manager_server.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = config_get('DATABASES')

for db_name, db_values in DATABASES.iteritems():
    for db_configname, db_value in db_values.iteritems():
        DATABASES[db_name][db_configname] = config_get('DATABASES_' + db_name.upper() + '_' + db_configname.upper(), DATABASES[db_name][db_configname])


EMAIL_FROM = config_get('EMAIL_FROM')
EMAIL_HOST = config_get('EMAIL_HOST', 'localhost')
EMAIL_HOST_USER = config_get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = config_get('EMAIL_HOST_PASSWORD', '')
EMAIL_PORT = config_get('EMAIL_PORT', 25)
EMAIL_SUBJECT_PREFIX = config_get('EMAIL_SUBJECT_PREFIX', '')
EMAIL_USE_TLS = config_get('EMAIL_USE_TLS', False)
EMAIL_USE_SSL = config_get('EMAIL_USE_SSL', False)
EMAIL_SSL_CERTFILE = config_get('EMAIL_SSL_CERTFILE', None)
EMAIL_SSL_KEYFILE = config_get('EMAIL_SSL_KEYFILE', None)
EMAIL_TIMEOUT = config_get('EMAIL_TIMEOUT', None)

YUBIKEY_CLIENT_ID = config_get('YUBIKEY_CLIENT_ID', None)
YUBIKEY_SECRET_KEY = config_get('YUBIKEY_SECRET_KEY', None)

EMAIL_BACKEND = config_get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
MAILGUN_ACCESS_KEY = config_get('MAILGUN_ACCESS_KEY', '')
MAILGUN_SERVER_NAME = config_get('MAILGUN_SERVER_NAME', '')

CACHE_ENABLE = config_get('CACHE_ENABLE', False)

if config_get('CACHE_DB', False):
    CACHES = {
        "default": {
            "BACKEND": 'django.core.cache.backends.db.DatabaseCache',
            "LOCATION": 'restapi_cache',
        }
    }

if config_get('CACHE_REDIS', False):
    CACHES = {
       "default": {
           "BACKEND": "django_redis.cache.RedisCache",
           "LOCATION": config_get('CACHE_REDIS_LOCATION', 'redis://localhost:6379/0'),
           "OPTIONS": {
               "CLIENT_CLASS": "django_redis.client.DefaultClient",
           }
       }
    }

if not config_get('THROTTLING', True):
    CACHES = {
        "default": {
            "BACKEND": 'django.core.cache.backends.dummy.DummyCache',
        }
    }

AUTH_KEY_LENGTH_BYTES = config_get('AUTH_KEY_LENGTH_BYTES', 64)
USER_PRIVATE_KEY_LENGTH_BYTES = config_get('USER_PRIVATE_KEY_LENGTH_BYTES', 80)
USER_PUBLIC_KEY_LENGTH_BYTES = config_get('USER_PUBLIC_KEY_LENGTH_BYTES', 32)
USER_SECRET_KEY_LENGTH_BYTES = config_get('USER_SECRET_KEY_LENGTH_BYTES', 80)
NONCE_LENGTH_BYTES = config_get('NONCE_LENGTH_BYTES', 24)
ACTIVATION_LINK_SECRET = config_get('ACTIVATION_LINK_SECRET')
DB_SECRET = config_get('DB_SECRET')
EMAIL_SECRET_SALT = config_get('EMAIL_SECRET_SALT')

ACTIVATION_LINK_TIME_VALID = config_get('ACTIVATION_LINK_TIME_VALID', 2592000) # in seconds
TOKEN_TIME_VALID = config_get('TOKEN_TIME_VALID', 86400) # in seconds
RECOVERY_VERIFIER_TIME_VALID = config_get('RECOVERY_VERIFIER_TIME_VALID', 600) # in seconds

DATABASE_ROUTERS = ['restapi.database_router.MainRouter']

TIME_SERVER = config_get('TIME_SERVER', 'time.google.com')

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, "static/")
STATIC_URL = '/static/'
