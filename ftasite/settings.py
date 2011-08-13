# Django settings for ors project.
import os
import sys
from localsettings import SECRET_KEY, FACEBOOK_APP_ID, FACEBOOK_API_KEY, FACEBOOK_SECRET_KEY, DATABASES, LOCALPATH, DEBUG, MEDIA_ROOT, STATIC_ROOT

sys.path.append(os.path.join(LOCALPATH, 'allbuttonspressed'))

TEMPLATE_DEBUG = DEBUG

ADMINS = (('Ray', 'razor2n4@gmail.com'), ('Razor', 'marceau.ray@gmail.com'))

MANAGERS = ADMINS

TIME_ZONE = 'America/New_York'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1

USE_I18N = True
USE_L10N = True

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
ADMIN_MEDIA_PREFIX = '/static/admin/'

STATICFILES_DIRS = (
    os.path.join(LOCALPATH, os.path.join('allbuttonspressed', 'static')),
    os.path.join(LOCALPATH, 'static'),
    os.path.join(os.path.dirname(__file__), 'static'),
)

# for django-mediagenerator
PRODUCTION_MEDIA_URL = '/media/'
DEV_MEDIA_URL = '/devmedia/'
GLOBAL_MEDIA_DIRS = STATICFILES_DIRS
GENERATED_MEDIA_DIR = os.path.join(LOCALPATH, '_generated_media')
GENERATED_MEDIA_NAMES_FILE = os.path.join(LOCALPATH, '_generated_media_names.py')

#EMAIL_HOST = 'smtp.gmail.com'
#EMAIL_HOST_PASSWORD = "newuser_22"
EMAIL_HOST_USER = 'feed.the.artists.2011@gmail.com'
EMAIL_HOST = 'smtp.com'
EMAIL_HOST_PASSWORD = "Newuser_2233"
#EMAIL_HOST_USER = "razor2n4@gmail.com"
EMAIL_USE_TLS = True
EMAIL_SUBJECT_PREFIX = "[FtA]"
EMAIL_PORT = 2525

SERVER_EMAIL = 'feed.the.artists.2011@gmail.com'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'autoload.middleware.AutoloadMiddleware',
    'mediagenerator.middleware.MediaMiddleware',
    'django.middleware.common.CommonMiddleware',
    'djangotoolbox.middleware.RedirectMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
#    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
#    'django.contrib.messages.middleware.MessageMiddleware',
    'socialregistration.middleware.FacebookMiddleware',
    'fbcanvas.middleware.CanvasMiddleware',
    'urlrouter.middleware.URLRouterFallbackMiddleware',
)

URL_ROUTE_HANDLERS = (
    'minicms.urlroutes.PageRoutes',
    'blog.urlroutes.BlogRoutes',
    'blog.urlroutes.BlogPostRoutes',
    'redirects.urlroutes.RedirectRoutes',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'minicms.context_processors.cms',
)

NON_REDIRECTED_PATHS = ('/admin/',)

ROOT_URLCONF = 'ftasite.urls'


TEMPLATE_DIRS = (
#    os.path.join(LOCALPATH, os.path.join('allbuttonspressed', 'templates')),
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
    'urlrouter',
    'minicms',
    'blog',
    'redirects',
    'simplesocial',
    'autoload',
    'djangotoolbox',
    'google_analytics',
    'google_cse',
    'disqus',
    'socialregistration',
    'mediagenerator',
    'fbcanvas',
#    'permission_backend_nonrel',
    'dbindexer',
#    'sentry',
#    'sentry.client',

)

AUTH_PROFILE_MODULE = 'nourish.UserProfile'
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'socialregistration.auth.FacebookAuth',
#    'permission_backend_nonrel.backends.NonrelPermissionBackend',
)
LOGIN_URL          = '/login/'
LOGIN_REDIRECT_URL = '/nourish/logged-in/'
LOGIN_ERROR_URL    = '/login-error/'


SOCIALREGISTRATION_USE_HTTPS = False
SOCIALREGISTRATION_GENERATE_USERNAME = True

FACEBOOK_REQUEST_PERMISSIONS = ''

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
    }
}

# Activate django-dbindexer if available
try:
    if 'native' not in DATABASES:
        import dbindexer
        DATABASES['native'] = DATABASES['default']
        DATABASES['default'] = {'ENGINE': 'dbindexer', 'TARGET': 'native', 'NAME': DATABASES['native']['NAME']}
        INSTALLED_APPS += ('dbindexer',)
        DBINDEXER_SITECONF = 'ftasite.dbindexes'
        MIDDLEWARE_CLASSES = ('dbindexer.middleware.DBIndexerMiddleware',) + \
                             MIDDLEWARE_CLASSES
except ImportError:
    pass

SITE_NAME = 'Feed The Artists'
SITE_DESCRIPTION = 'Feeding Artists'
SITE_COPYRIGHT = '2011'

DISQUS_SHORTNAME = ''
GOOGLE_ANALYTICS_ID = ''
GOOGLE_CUSTOM_SEARCH_ID = ''
TWITTER_USERNAME = ''

MEDIA_BUNDLES = (
    ('main.css',
        'design.sass',
        'rest.css',
    ),
    ('artistGrid.js',
        'js/artistGrid.js',
    ),
    ('reports.js',
        'js/reports.js',
    ),
    ('nourish.css',
        'nourish.css',
    ),
    ('base.css',
        'base.css',
    ),
    ('site.css',
        'site.css',
    ),
    ('canvas.css',
        'canvas.css',
    ),
)

MEDIA_DEV_MODE = DEBUG
