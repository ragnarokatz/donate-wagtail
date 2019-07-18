"""
Django settings for donate project.
"""
import os
import environ
import logging.config
import dj_database_url

app = environ.Path(__file__) - 1
root = app - 1

# We set defaults for values that aren't security related
# to the least permissive setting. For security related values,
# we rely on it being explicitly set (no default values) so that
# we error out first.
env = environ.Env(
    ALLOWED_HOSTS=(list, []),
    ASSET_DOMAIN=(str, ''),
    AWS_LOCATION=(str, ''),
    CONTENT_TYPE_NO_SNIFF=bool,
    CORS_REGEX_WHITELIST=(tuple, ()),
    CORS_WHITELIST=(tuple, ()),
    DATABASE_URL=(str, None),
    DEBUG=(bool, False),
    DJANGO_LOG_LEVEL=(str, 'INFO'),
    HEROKU_APP_NAME=(str, ''),
    SET_HSTS=bool,
    SSL_REDIRECT=bool,
    USE_S3=(bool, True),
    USE_X_FORWARDED_HOST=(bool, False),
    XSS_PROTECTION=bool,
    REDIS_URL=(str, ''),
    RANDOM_SEED=(int, None),
    # Braintree
    BRAINTREE_USE_SANDBOX=(bool, True),
    BRAINTREE_MERCHANT_ID=(str, ''),
    BRAINTREE_PUBLIC_KEY=(str, ''),
    BRAINTREE_PRIVATE_KEY=(str, ''),
    BRAINTREE_TOKENIZATION_KEY=(str, ''),
)

# Read in the environment
if os.path.exists(f'{root}/.env') is True:
    environ.Env.read_env(f'{root}/.env')
else:
    environ.Env.read_env()


SECRET_KEY = env('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env('ALLOWED_HOSTS')
CSRF_TRUSTED_ORIGINS = ALLOWED_HOSTS
USE_X_FORWARDED_HOST = env('USE_X_FORWARDED_HOST')

HEROKU_APP_NAME = env('HEROKU_APP_NAME')

if HEROKU_APP_NAME:
    ALLOWED_HOSTS.append(HEROKU_APP_NAME + '.herokuapp.com')

INSTALLED_APPS = [
    'donate.users',
    'donate.core',
    'donate.payments',

    'wagtail.contrib.settings',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail.core',

    'modelcluster',
    'taggit',
    'storages',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'wagtail.core.middleware.SiteMiddleware',
]

ROOT_URLCONF = 'donate.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': [
            app('templates'),
        ],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'wagtail.contrib.settings.context_processors.settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'donate.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': root('db.sqlite3'),
    }
}

DATABASE_URL = env('DATABASE_URL')

if DATABASE_URL is not None:
    DATABASES['default'].update(dj_database_url.config())

DATABASES['default']['ATOMIC_REQUESTS'] = True

if env('REDIS_URL'):
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': env('REDIS_URL'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                # timeout for read/write operations after a connection is established
                'SOCKET_TIMEOUT': 120,
                # timeout for the connection to be established
                'SOCKET_CONNECT_TIMEOUT': 30,
                # Enable compression
                'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
                # Ignore exceptions, redis only used for caching (i.e. if redis fails, will use database)
                'IGNORE_EXCEPTIONS': True
            }
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
        }
    }

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

LANGUAGE_CODE = 'en'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_ROOT = app('frontend')
WHITENOISE_INDEX_FILE = True

STATIC_ROOT = root('static')
STATIC_URL = '/static/'

# Storage for user generated files
USE_S3 = env('USE_S3')
if USE_S3:
    # Use S3 to store user files if the corresponding environment var is set
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_CUSTOM_DOMAIN = env('AWS_S3_CUSTOM_DOMAIN')
    AWS_LOCATION = env('AWS_LOCATION')
    MEDIA_URL = 'https://' + AWS_S3_CUSTOM_DOMAIN + '/'
    MEDIA_ROOT = ''
    # This is a workaround for https://github.com/wagtail/wagtail/issues/3206
    AWS_S3_FILE_OVERWRITE = False
else:
    # Otherwise use the default filesystem storage
    MEDIA_ROOT = root('media/')
    MEDIA_URL = '/media/'


# Remove the default Django loggers and configure new ones
LOGGING_CONFIG = None
LOGGING = {
    'version': 1,
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        }
    },
    'formatters': {
        'verbose': {
            'format': '%(asctime)s [%(levelname)s] %(message)s'
        }
    },
    'handlers': {
        'debug': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'filters': ['require_debug_true'],
            'formatter': 'verbose'
        },
        'error': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler'
        },
        'debug-error': {
            'level': 'ERROR',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler'
        },
        'info': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['debug'],
            'level': 'DEBUG'
        },
        'django.server': {
            'handlers': ['debug'],
            'level': 'DEBUG',
        },
        'django.request': {
            'handlers': ['error'],
            'propagate': False,
            'level': 'ERROR'
        },
        'django.template': {
            'handlers': ['debug-error'],
            'level': 'ERROR'
        },
        'django.db.backends': {
            'handlers': ['debug-error'],
            'level': 'ERROR'
        },
        'django.utils.autoreload': {
            'handlers': ['debug-error'],
            'level': 'ERROR'
        },
        'donate': {
            'handlers': ['info'],
            'level': 'INFO',
        }
    }
}
DJANGO_LOG_LEVEL = env('DJANGO_LOG_LEVEL')
logging.config.dictConfig(LOGGING)

# CSP
CSP_DEFAULT = (
    '\'self\''
)

CSP_DEFAULT_SRC = env('CSP_DEFAULT_SRC', default=CSP_DEFAULT)
CSP_SCRIPT_SRC = env('CSP_SCRIPT_SRC', default=CSP_DEFAULT)
CSP_IMG_SRC = env('CSP_IMG_SRC', default=CSP_DEFAULT)
CSP_OBJECT_SRC = env('CSP_OBJECT_SRC', default=None)
CSP_MEDIA_SRC = env('CSP_MEDIA_SRC', default=None)
CSP_FRAME_SRC = env('CSP_FRAME_SRC', default=None)
CSP_FONT_SRC = env('CSP_FONT_SRC', default=CSP_DEFAULT)
CSP_CONNECT_SRC = env('CSP_CONNECT_SRC', default=None)
CSP_STYLE_SRC = env('CSP_STYLE_SRC', default=CSP_DEFAULT)
CSP_BASE_URI = env('CSP_BASE_URI', default=None)
CSP_CHILD_SRC = env('CSP_CHILD_SRC', default=None)
CSP_FRAME_ANCESTORS = env('CSP_FRAME_ANCESTORS', default=None)
CSP_FORM_ACTION = env('CSP_FORM_ACTION', default=None)
CSP_SANDBOX = env('CSP_SANDBOX', default=None)
CSP_REPORT_URI = env('CSP_REPORT_URI', default=None)
CSP_WORKER_SRC = env('CSP_WORKER_SRC', default=CSP_DEFAULT)

# Security
SECURE_BROWSER_XSS_FILTER = env('XSS_PROTECTION')
SECURE_CONTENT_TYPE_NOSNIFF = env('CONTENT_TYPE_NO_SNIFF')
SECURE_HSTS_INCLUDE_SUBDOMAINS = env('SET_HSTS')
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 31 * 6
SECURE_SSL_REDIRECT = env('SSL_REDIRECT')
# Heroku goes into an infinite redirect loop without this.
# See https://docs.djangoproject.com/en/1.10/ref/settings/#secure-ssl-redirect
if env('SSL_REDIRECT') is True:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

X_FRAME_OPTIONS = env('X_FRAME_OPTIONS')
REFERRER_POLICY = 'no-referrer-when-downgrade'

AUTH_USER_MODEL = 'users.User'

RANDOM_SEED = env('RANDOM_SEED')

# Braintree
BRAINTREE_USE_SANDBOX = env('BRAINTREE_USE_SANDBOX')
BRAINTREE_MERCHANT_ID = env('BRAINTREE_MERCHANT_ID')
BRAINTREE_PUBLIC_KEY = env('BRAINTREE_PUBLIC_KEY')
BRAINTREE_PRIVATE_KEY = env('BRAINTREE_PRIVATE_KEY')
BRAINTREE_TOKENIZATION_KEY = env('BRAINTREE_TOKENIZATION_KEY')

# Wagtail settings

# This name is displayed in the Wagtail admin.
WAGTAIL_SITE_NAME = "donate"
