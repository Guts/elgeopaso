# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Base settings to build other settings files upon.
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Django
from django.core.exceptions import ImproperlyConfigured

# 3rd party
import environ

# ##############################################################################
# ########## Globals ###############
# ##################################
ROOT_DIR = environ.Path(__file__) - 3  # (elgeopaso/settings/base.py - 2 = elgeopaso/)
APPS_DIR = ROOT_DIR.path("elgeopaso")

env = environ.Env()

READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=True)
if READ_DOT_ENV_FILE:
    # OS environment variables take precedence over variables from .env
    env.read_env(str(ROOT_DIR.path(".env")))

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/fr/2.2/ref/settings/#debug
DEBUG = env.bool("DJANGO_DEBUG", False)
# Local time zone. Choices are
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# though not all of them may be available with every OS.
# In Windows, this must be set to your system time zone.
TIME_ZONE = "Europe/Paris"
# https://docs.djangoproject.com/fr/2.2/ref/settings/#language-code
LANGUAGE_CODE = "fr-fr"
# https://docs.djangoproject.com/fr/2.2/ref/settings/#site-id
SITE_ID = 1
# https://docs.djangoproject.com/fr/2.2/ref/settings/#use-i18n
USE_I18N = True
# https://docs.djangoproject.com/fr/2.2/ref/settings/#use-l10n
USE_L10N = True
# https://docs.djangoproject.com/fr/2.2/ref/settings/#use-tz
USE_TZ = True
# https://docs.djangoproject.com/fr/2.2/ref/settings/#locale-paths
LOCALE_PATHS = [ROOT_DIR.path("locale")]

# DATABASES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/fr/2.2/ref/settings/#databases
try:
    DATABASES = {
        # read os.environ['DATABASE_URL'] and raises ImproperlyConfigured exception if not found
        "default": env.db("DATABASE_URL"),
        # read os.environ['SQLITE_URL']
        "extra": env.db("SQLITE_URL", default="sqlite:////tmp/my-tmp-sqlite.db"),
    }
except ImproperlyConfigured:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": str(ROOT_DIR.path("local-db.sqlite3")),
        }
    }

DATABASES["default"]["ATOMIC_REQUESTS"] = True
# DATABASES["default"]["OPTIONS"]["connect_timeout"] = 30

# URLS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/fr/2.2/ref/settings/#root-urlconf
ROOT_URLCONF = "elgeopaso.urls"
# https://docs.djangoproject.com/fr/2.2/ref/settings/#wsgi-application
WSGI_APPLICATION = "elgeopaso.wsgi.application"

# APPS
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.humanize",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.forms",
]

THIRD_PARTY_APPS = [
    "ckeditor",
    "ckeditor_uploader",
    "rest_framework",
    "rest_framework_filters",
    "django_filters",
    "widget_tweaks",
]

PROJECT_APPS = [
    "accounts.apps.AccountsConfig",
    "api.apps.ApiConfig",
    "cms.apps.CmsConfig",
    "jobs.apps.JobsConfig",
]
# https://docs.djangoproject.com/fr/2.2/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + PROJECT_APPS


# PASSWORDS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/fr/2.2/ref/settings/#password-hashers
PASSWORD_HASHERS = [
    # https://docs.djangoproject.com/fr/2.2/topics/auth/passwords/#using-argon2-with-django
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]
# https://docs.djangoproject.com/fr/2.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# MIDDLEWARE
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/fr/2.2/ref/settings/#middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.common.BrokenLinkEmailsMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# STATICS (CSS, JavaScript, Images)
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_ROOT = str(ROOT_DIR("static"))
STATIC_URL = "/static/"
# https://docs.djangoproject.com/fr/2.2/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [str(ROOT_DIR("assets"))]
# https://docs.djangoproject.com/fr/2.2/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# MEDIA
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/fr/2.2/ref/settings/#media-root
MEDIA_ROOT = str(ROOT_DIR("uploads"))
# https://docs.djangoproject.com/fr/2.2/ref/settings/#media-url
MEDIA_URL = "/media/"


# TEMPLATES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/fr/2.2/ref/settings/#templates
TEMPLATES = [
    {
        # https://docs.djangoproject.com/fr/2.2/ref/settings/#std:setting-TEMPLATES-BACKEND
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # https://docs.djangoproject.com/fr/2.2/ref/settings/#template-dirs
        "DIRS": [str(APPS_DIR.path("templates"))],
        "OPTIONS": {
            # https://docs.djangoproject.com/fr/2.2/ref/settings/#template-loaders
            # https://docs.djangoproject.com/fr/2.2/ref/templates/api/#loader-types
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]


# SECURITY
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/fr/2.2/ref/settings/#session-cookie-httponly
SESSION_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/fr/2.2/ref/settings/#csrf-cookie-httponly
CSRF_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/fr/2.2/ref/settings/#secure-browser-xss-filter
SECURE_BROWSER_XSS_FILTER = True
# https://docs.djangoproject.com/fr/2.2/ref/settings/#x-frame-options
X_FRAME_OPTIONS = "DENY"


# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/fr/2.2/ref/settings/#email-backend
EMAIL_BACKEND = env(
    "DJANGO_EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
)
# https://docs.djangoproject.com/en/2.2/ref/settings/#email-timeout
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_TIMEOUT = 5
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env("SMTP_USER", default="elpaso@georezo.net")
EMAIL_HOST_PASSWORD = env("SMTP_PSWD", default="elpaso@georezo.net")
RECIPIENTS = env("REPORT_REPORT_RECIPIENTS", default="elpaso@georezo.net")

# ADMIN
# ------------------------------------------------------------------------------
# Django Admin URL.
ADMIN_URL = "admin/"
# https://docs.djangoproject.com/fr/2.2/ref/settings/#admins
ADMINS = [("""Julien Moura""", "elpaso@georezo.net")]
# https://docs.djangoproject.com/fr/2.2/ref/settings/#managers
MANAGERS = ADMINS

# LOGGING
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/fr/2.2/ref/settings/#logging
# See https://docs.djangoproject.com/fr/2.2/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s "
            "%(process)d %(thread)d %(message)s"
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        }
    },
    "root": {"level": "INFO", "handlers": ["console"]},
}

# THIRD-PARTY APPS ##
# ------------------------------------------------------------------------------

# CMS - CK EDITOR
CKEDITOR_UPLOAD_PATH = "ck_uploads"
CKEDITOR_IMAGE_BACKEND = "pillow"
IMAGE_QUALITY = 75
THUMBNAIL_SIZE = (300, 300)

# CKEDITOR_FILENAME_GENERATOR = 'utils.get_filename'
CKEDITOR_ALLOW_NONIMAGE_FILES = False
CKEDITOR_RESTRICT_BY_DATE = False
CKEDITOR_BROWSE_SHOW_DIRS = True
CKEDITOR_CONFIGS = {
    "default": {
        "toolbar": "Standard",
        "height": 400,
        "width": "100%",
        "language": "fr",
        "removePlugins": " bidi,flash,forms,language,scayt,wsc,",
        "extraPlugins": "uploadimage,uploadwidget,",
    },
}

# Django REST Framework (API)
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "PAGE_SIZE": 20,
}


# ===========================================================================
# APPS SETTINGS
# ===========================================================================

# JOBS
CRAWL_FREQUENCY = "hourly"
CRAWL_RSS_SIZE = 200
FIXTURE_DIRS = ("/jobs/fixtures/",)
