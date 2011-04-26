import os
import logging, logging.handlers

import environment
import logconfig

# If using a separate Python package (e.g. a submodule in vendor/) to share
# logic between applications, you can also share settings. Just create another
# settings file in your package and import it like so:
#
#     from comrade.core.settings import * 
#
# The top half of this settings.py file is copied from comrade for clarity. We
# use the import method in actual deployments.

# Make filepaths relative to settings.
path = lambda root,*a: os.path.join(root, *a)
ROOT = os.path.dirname(os.path.abspath(__file__))


# List of admin e-mails - we use Hoptoad to collect error notifications, so this
# is usually blank.
ADMINS = ()
MANAGERS = ADMINS

# Deployment Configuration

class DeploymentType:
    PRODUCTION = "PRODUCTION"
    DEV = "DEV"
    SOLO = "SOLO"
    STAGING = "STAGING"
    dict = {
        SOLO: 1,
        PRODUCTION: 2,
        DEV: 3,
        STAGING: 4
    }

if 'DEPLOYMENT_TYPE' in os.environ:
    DEPLOYMENT = os.environ['DEPLOYMENT_TYPE'].upper()
else:
    DEPLOYMENT = DeploymentType.SOLO

def is_solo():
    return DEPLOYMENT == DeploymentType.SOLO

SITE_ID = DeploymentType.dict[DEPLOYMENT]

DEBUG = DEPLOYMENT != DeploymentType.PRODUCTION
STATIC_MEDIA_SERVER = is_solo()
TEMPLATE_DEBUG = DEBUG
SSL_ENABLED = not DEBUG

INTERNAL_IPS = ('127.0.0.1',)

# Logging

if DEBUG:
    LOG_LEVEL = logging.DEBUG
else:
    LOG_LEVEL = logging.INFO

# Only log to syslog if this is not a solo developer server.
USE_SYSLOG = not is_solo()

# Cache Backend

CACHE_TIMEOUT = 3600
MAX_CACHE_ENTRIES = 10000
CACHE_MIDDLEWARE_SECONDS = 3600
CACHE_MIDDLEWARE_KEY_PREFIX = ''

# Don't require developers to install memcached, and also make debugging easier
# because cache is automatically wiped when the server reloads.
if is_solo():
    CACHE_BACKEND = ('locmem://?timeout=%(CACHE_TIMEOUT)d'
            '&max_entries=%(MAX_CACHE_ENTRIES)d' % locals())
else:
    CACHE_BACKEND = ('memcached://127.0.0.1:11211/?timeout=%(CACHE_TIMEOUT)d'
            '&max_entries=%(MAX_CACHE_ENTRIES)d' % locals())

# E-mail Server

if is_solo():
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_HOST_USER = 'YOU@YOUR-SITE.com'
    EMAIL_HOST_PASSWORD = 'PASSWORD'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True

DEFAULT_FROM_EMAIL = "Bueda Support <support@bueda.com>"

CONTACT_EMAIL = 'support@bueda.com'

# Internationalization

TIME_ZONE = 'UTC'
LANGUAGE_CODE = 'en-us'
USE_I18N = False

# Testing & Coverage

# Use nosetests instead of unittest
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

COVERAGE_REPORT_HTML_OUTPUT_DIR = 'coverage'
COVERAGE_MODULE_EXCLUDES = ['tests$', 'settings$', 'urls$', 'vendor$',
        '__init__', 'migrations', 'templates', 'django', 'debug_toolbar',
        'core\.fixtures', 'users\.fixtures',]

try:
    import multiprocessing
    cpu_count = multiprocessing.cpu_count()
except ImportError:
    cpu_count = 1

NOSE_ARGS = ['--logging-clear-handlers', '--processes=%s' % cpu_count]

if is_solo():
    try:
        os.mkdir(COVERAGE_REPORT_HTML_OUTPUT_DIR)
    except OSError:
        pass

# Paths

MEDIA_ROOT = path(ROOT, 'media')
MEDIA_URL = '/media/'
ADMIN_MEDIA_PREFIX = '/media/admin'
ROOT_URLCONF = 'urls'

# Version Information

# Grab the current commit SHA from git - handy for confirming the version
# deployed on a remote server is the one you think it is.
import subprocess
GIT_COMMIT = subprocess.Popen(['git', 'rev-parse', '--short', 'HEAD'],
    stdout=subprocess.PIPE).communicate()[0].strip()
del subprocess

# Database

DATABASES = {}

if DEPLOYMENT == DeploymentType.PRODUCTION:
    DATABASES['default'] = {
        'NAME': 'boilerplate',
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'your-database.com',
        'PORT': '',
        'USER': 'boilerplate',
        'PASSWORD': 'your-password'
    }
elif DEPLOYMENT == DeploymentType.DEV:
    DATABASES['default'] = {
        'NAME': 'boilerplate_dev',
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'your-database.com',
        'PORT': '',
        'USER': 'boilerplate',
        'PASSWORD': 'your-password'
    }
elif DEPLOYMENT == DeploymentType.STAGING:
    DATABASES['default'] = {
        'NAME': 'boilerplate_staging',
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'your-database.com',
        'PORT': '',
        'USER': 'boilerplate',
        'PASSWORD': 'your-password'
    }
else:
    DATABASES['default'] = {
        'NAME': 'db',
        'ENGINE': 'django.db.backends.sqlite3',
        'HOST': '',
        'PORT': '',
        'USER': '',
        'PASSWORD': ''
    }

# Message Broker (for Celery)

BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = "boilerplate"
BROKER_PASSWORD = "boilerplate"
BROKER_VHOST = "boilerplate"
CELERY_RESULT_BACKEND = "amqp"

# Run tasks eagerly in development, so developers don't have to keep a celeryd
# processing running.
CELERY_ALWAYS_EAGER = is_solo()
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

# South

# Speed up testing when you have lots of migrations.
SOUTH_TESTS_MIGRATE = False
SKIP_SOUTH_TESTS = True

# Logging

SYSLOG_FACILITY = logging.handlers.SysLogHandler.LOG_LOCAL0
SYSLOG_TAG = "boilerplate"

# See PEP 391 and logconfig.py for formatting help.  Each section of LOGGING
# will get merged into the corresponding section of log_settings.py.
# Handlers and log levels are set up automatically based on LOG_LEVEL and DEBUG
# unless you set them here.  Messages will not propagate through a logger
# unless propagate: True is set.
LOGGERS = {
    'loggers': {
        'boilerplate': {},
    },
}

logconfig.initialize_logging(SYSLOG_TAG, SYSLOG_FACILITY, LOGGERS, LOG_LEVEL,
        USE_SYSLOG)

# Debug Toolbar

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False
}

# Application Settings

SECRET_KEY = 'TODO-generate-a-new-secret-key'

LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = '/'

# Sessions

SESSION_ENGINE = "django.contrib.sessions.backends.cache"

# Middleware

middleware_list = [
    'commonware.log.ThreadRequestMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'comrade.core.middleware.HttpMethodsMiddleware',
]

if is_solo():
    middleware_list += [
        'comrade.core.middleware.ArgumentLogMiddleware',
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ]
else:
    middleware_list += [
        'django.middleware.transaction.TransactionMiddleware',
        'commonware.middleware.SetRemoteAddrFromForwardedFor',
    ]

MIDDLEWARE_CLASSES = tuple(middleware_list)

# Templates

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

if not is_solo():
    TEMPLATE_LOADERS = (
        ('django.template.loaders.cached.Loader', TEMPLATE_LOADERS),
    )

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.request',
    'django.core.context_processors.csrf',
    'django.core.context_processors.media',
    'django.contrib.messages.context_processors.messages',

    'comrade.core.context_processors.default',
    'django.core.context_processors.media',
)

TEMPLATE_DIRS = (
    path(ROOT, 'templates')
)

apps_list = [
        'django.contrib.auth',
        'django.contrib.admin',
        'django.contrib.contenttypes',
        'django.contrib.sites',
        'django.contrib.markup',
        'django.contrib.messages',

        #'your',
        #'apps',
        #'here',
        'foo',
]

if is_solo():
    apps_list += [
        'django_extensions',
        'debug_toolbar',
        'django_nose',
        'django_coverage',
    ]

INSTALLED_APPS = tuple(apps_list)
