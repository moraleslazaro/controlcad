# Django settings for ControlCAD project.
from os import environ
from os import path

# ControlCAD base directory used for automatic configuration.
BASE_DIR = environ['BASE_DIR'].replace('\\', '/')

# ControlCAD version
CONTROLCAD_VERSION = 1.0

# ControlCAD Paginator items per page for listing pages.
ITEMS_PER_PAGE = 20

# Custom user model for authentication, this option will replace
# the default 'django.contrib.auth.models.User' model in Django
# auth/auth system.
AUTH_USER_MODEL = 'admin.User'

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Lazaro Morales', 'lazaro@frioclima.com.cu'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': path.join(BASE_DIR, 'database', 'database.sqlite3'),
    },
    #'bdfrioclima': {
        #'ENGINE': 'sqlserver_ado',
        #'HOST': '192.168.146.128,1433',
        #'USER': 'sa',
        #'PASSWORD': 'abc123',
        #'NAME': 'FABRICABD',
        #'OPTIONS': {
            #'provider': 'SQLOLEDB'
        #},
    #}
}

# Router used to connect with MSSQL2000
DATABASE_ROUTERS = ['controlcad.routers.MSSQLRouter']

# List of locations of the fixture data files.
FIXTURE_DIRS = (
    path.join(BASE_DIR, 'fixtures'),
)

# Login page URL used to authenticate users.
LOGIN_URL = '/login'

# Redirect here after successfully authenticate a user.
LOGIN_REDIRECT_URL = '/'

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['localhost']

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Havana'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    path.join(BASE_DIR, 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '+%i%a9_elk1nlk$t3ctqy&bs$24d81sz60bja)0#!y@nx4^%a1'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.messages.context_processors.messages',
    'django.contrib.auth.context_processors.auth',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'controlcad.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'controlcad.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or
    # "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    path.join(BASE_DIR, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    'cad',
    'scan',
    'admin',
    'condis',
)
