# -*- coding: utf-8 -*-
#! python3  # noqa: E265

"""
    Base settings to build other settings files upon.
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard
import pathlib
from os import getenv

# Django
from django.core.exceptions import ImproperlyConfigured

# 3rd party
import dj_database_url

# project
from elgeopaso import __about__

# ##############################################################################
# ########## Globals ###############
# ##################################
ROOT_DIR = pathlib.Path(__file__).parents[2].resolve()
PROJ_DIR = ROOT_DIR / getenv("DJANGO_PROJECT_FOLDER", default="elgeopaso")

# GENERAL
# ------------------------------------------------------------------------------

# some metadata
PROJECT_VERSION = __about__.__version__
USER_AGENT = "{}/{} +https://elgeopaso.georezo.net/".format(
    __about__.__title_clean__, PROJECT_VERSION
)

# https://docs.djangoproject.com/fr/2.2/ref/settings/#debug
DEBUG = getenv("DJANGO_DEBUG", default="0")
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
LOCALE_PATHS = [ROOT_DIR / "locale"]

# DATABASES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/fr/2.2/ref/settings/#databases
try:
    DATABASES = {
        # read os.environ['DATABASE_URL'] and raises ImproperlyConfigured exception if not found
        # "default": env.db("DATABASE_URL", default="sqlite:///local-db.sqlite3"),
        "default": dj_database_url.config(
            env="DATABASE_URL", default="sqlite:///local-db.sqlite3", conn_max_age=300
        )
    }
except ImproperlyConfigured:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": str(ROOT_DIR / "local-db.sqlite3"),
        }
    }

DATABASES["default"]["ATOMIC_REQUESTS"] = True

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
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    "django.forms",
]

THIRD_PARTY_APPS = [
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "ckeditor",
    "ckeditor_uploader",
    "crispy_forms",
    "rest_framework",
    "rest_framework_filters",
    "drf_yasg",
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

STATIC_ROOT = str(ROOT_DIR / "static")
STATIC_URL = "/static/"
# https://docs.djangoproject.com/fr/2.2/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [str(ROOT_DIR / "assets")]
# https://docs.djangoproject.com/fr/2.2/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# MEDIA
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/fr/2.2/ref/settings/#media-root
MEDIA_ROOT = str(ROOT_DIR / "uploads")
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
        "DIRS": [str(PROJ_DIR / "templates")],
        "OPTIONS": {
            # https://docs.djangoproject.com/fr/2.2/ref/settings/#template-loaders
            # https://docs.djangoproject.com/fr/2.2/ref/templates/api/#loader-types
            # "loaders": [
            #     "django.template.loaders.cached.Loader"
            #     "django.template.loaders.app_directories.Loader",
            #     "django.template.loaders.filesystem.Loader",
            # ],
            "loaders": [
                (
                    "django.template.loaders.cached.Loader",
                    [
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader",
                    ],
                ),
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

# AUTHENTICATION
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/fr/2.2/ref/settings/#auth
AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

# https://docs.djangoproject.com/fr/2.2/ref/settings/#login-url
LOGIN_REDIRECT_URL = None  # if None, then the previous page will be used

# https://docs.djangoproject.com/fr/2.2/ref/settings/#std:setting-SITE_ID
SITE_ID = 1  # required by Django AllAuth

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/fr/2.2/ref/settings/#email-backend
EMAIL_BACKEND = getenv(
    "DJANGO_EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
)
# https://docs.djangoproject.com/en/2.2/ref/settings/#email-timeout
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_TIMEOUT = 5
EMAIL_USE_TLS = True
EMAIL_HOST_USER = getenv("SMTP_USER", default="elpaso@georezo.net")
EMAIL_HOST_PASSWORD = getenv("SMTP_PSWD", default="")
REPORT_RECIPIENTS = getenv("REPORT_RECIPIENTS", default="elpaso@georezo.net,").split(
    ","
)

# ADMIN
# ------------------------------------------------------------------------------
# Django Admin URL.
ADMIN_URL = "admin/"
# https://docs.djangoproject.com/fr/2.2/ref/settings/#admins
ADMINS = [("Julien Moura", "elpaso@georezo.net")]
# https://docs.djangoproject.com/fr/2.2/ref/settings/#managers
MANAGERS = ADMINS

# LOGGING
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/fr/2.2/ref/settings/#logging
# See https://docs.djangoproject.com/fr/2.2/topics/logging for
# more details on how to customize your logging configuration.
LOG_FORMAT = (
    "%(asctime)s || %(levelname)s "
    "|| %(process)d %(thread)d "
    "|| %(module)s - %(lineno)d "
    "|| %(funcName)s || %(message)s"
)


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"verbose": {"format": LOG_FORMAT}},
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

# CRISPY FORMS
# http://django-crispy-forms.readthedocs.io/en/latest/install.html#template-packs
CRISPY_TEMPLATE_PACK = "bootstrap3"

# DJANGO ALLAUTH
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_ALLOW_REGISTRATION = int(
    getenv("DJANGO_ACCOUNT_ALLOW_REGISTRATION", default="1")
)
ACCOUNT_AUTHENTICATION_METHOD = "username"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 1
# ACCOUNT_ADAPTER = "django_starter.users.adapters.AccountAdapter"
# SOCIALACCOUNT_ADAPTER = "django_starter.users.adapters.SocialAccountAdapter"

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

# OpenAPI
SWAGGER_SETTINGS = {
    "DEEP_LINKING": True,
    "REFETCH_SCHEMA_WITH_AUTH": True,
    "REFETCH_SCHEMA_ON_LOGOUT": True,
    "TAGS_SORTER": "alpha",
}

# ===========================================================================
# APPS SETTINGS
# ===========================================================================

# JOBS
CRAWL_FREQUENCY = "hourly"
CRAWL_RSS_SIZE = 100
FIXTURE_DIRS = ("/jobs/fixtures/",)
