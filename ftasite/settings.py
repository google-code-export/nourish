# Django settings for ors project.
import os
from localsettings import SECRET_KEY, FACEBOOK_APP_ID, FACEBOOK_API_KEY, FACEBOOK_SECRET_KEY, DATABASES, LOCALPATH

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = ()

MANAGERS = ADMINS

TIME_ZONE = 'America/New_York'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1

USE_I18N = True
USE_L10N = True

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
ADMIN_MEDIA_PREFIX = '/static/admin/'

MEDIA_ROOT = '/home/marcus/fta/media'
STATIC_ROOT = '/home/marcus/fta/static/'

STATICFILES_DIRS = ()

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
#    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
#    'django.contrib.messages.middleware.MessageMiddleware',
    'socialregistration.middleware.FacebookMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
)

ROOT_URLCONF = 'ftasite.urls'

TEMPLATE_DIRS = (
    os.path.join(LOCALPATH, 'templates'),
    os.path.join(os.path.dirname(__file__), 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'nourish',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'djangotoolbox',
    'socialregistration',
    'django_yuml',
)

AUTH_PROFILE_MODULE = 'nourish.UserProfile'
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'socialregistration.auth.FacebookAuth',
)
LOGIN_URL          = '/login/'
LOGIN_REDIRECT_URL = '/nourish/logged-in/'
LOGIN_ERROR_URL    = '/login-error/'


SOCIALREGISTRATION_USE_HTTPS = False
SOCIALREGISTRATION_GENERATE_USERNAME = True

FACEBOOK_REQUEST_PERMISSIONS = ''

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
    },
    'loggers': {
        'django.request': {
            'handlers': [],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# Activate django-dbindexer if available
try:
    if 'native' not in DATABASES:
        import dbindexer
        DATABASES['native'] = DATABASES['default']
        DATABASES['default'] = {'ENGINE': 'dbindexer', 'TARGET': 'native'}
        INSTALLED_APPS += ('dbindexer',)
        DBINDEXER_SITECONF = 'ors.dbindexes'
        MIDDLEWARE_CLASSES = ('dbindexer.middleware.DBIndexerMiddleware',) + \
                             MIDDLEWARE_CLASSES
except ImportError:
    pass
