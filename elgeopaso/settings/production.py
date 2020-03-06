# -*- coding: UTF-8 -*-
#! python3  # noqa: E265

"""
    Settings built upon base for production.
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
from os import getenv

# 3rd party
import dj_database_url

# common settings
from .base import *  # noqa

# ##############################################################################
# ########## Globals ###############
# ##################################
# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/fr/2.2/ref/settings/#secret-key
SECRET_KEY = getenv("DJANGO_SECRET_KEY")
# https://docs.djangoproject.com/fr/2.2/ref/settings/#allowed-hosts
ALLOWED_HOSTS = getenv("DJANGO_ALLOWED_HOSTS", default="elgeopaso.georezo.net, ").split(
    ", "
)

# DATABASES
# ------------------------------------------------------------------------------
DATABASES["default"] = dj_database_url.config(env="DATABASE_URL")  # noqa F405
DATABASES["default"]["ATOMIC_REQUESTS"] = True  # noqa F405
DATABASES["default"]["CONN_MAX_AGE"] = int(  # noqa F405
    getenv("CONN_MAX_AGE", default="60")
)

# CACHES
# ------------------------------------------------------------------------------
CACHE_DIR = ROOT_DIR / "_cache"  # noqa: F405
CACHE_DIR.mkdir(exist_ok=True)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": CACHE_DIR,
        "KEY_PREFIX": "elgeopaso_",
        "TIMEOUT": 1800,
    }
}

# SECURITY
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/fr/2.2/ref/settings/#secure-proxy-ssl-header
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# https://docs.djangoproject.com/fr/2.2/ref/settings/#secure-ssl-redirect
SECURE_SSL_REDIRECT = int(getenv("DJANGO_SECURE_SSL_REDIRECT", default=True))
# https://docs.djangoproject.com/fr/2.2/ref/settings/#session-cookie-secure
SESSION_COOKIE_SECURE = True
# https://docs.djangoproject.com/fr/2.2/ref/settings/#csrf-cookie-secure
CSRF_COOKIE_SECURE = True
# https://docs.djangoproject.com/fr/2.2/topics/security/#ssl-https
# https://docs.djangoproject.com/fr/2.2/ref/settings/#secure-hsts-seconds
# TODO: set this to 60 seconds first and then to 518400 once you prove the former works
SECURE_HSTS_SECONDS = 60
# https://docs.djangoproject.com/fr/2.2/ref/settings/#secure-hsts-include-subdomains
SECURE_HSTS_INCLUDE_SUBDOMAINS = int(
    getenv("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True)
)
# https://docs.djangoproject.com/fr/2.2/ref/settings/#secure-hsts-preload
SECURE_HSTS_PRELOAD = int(getenv("DJANGO_SECURE_HSTS_PRELOAD", default=True))
# https://docs.djangoproject.com/fr/2.2/ref/middleware/#x-content-type-options-nosniff
SECURE_CONTENT_TYPE_NOSNIFF = int(
    getenv("DJANGO_SECURE_CONTENT_TYPE_NOSNIFF", default=True)
)

# STATIC
# ------------------------
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# MEDIA
# ------------------------------------------------------------------------------

# TEMPLATES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/fr/2.2/ref/settings/#templates
TEMPLATES[-1]["OPTIONS"]["loaders"] = [  # type: ignore[index] # noqa F405
    (
        "django.template.loaders.cached.Loader",
        [
            "django.template.loaders.filesystem.Loader",
            "django.template.loaders.app_directories.Loader",
        ],
    )
]

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/fr/2.2/ref/settings/#default-from-email
DEFAULT_FROM_EMAIL = getenv(
    "DJANGO_DEFAULT_FROM_EMAIL", default="El Géo Paso <elpaso@georezo.net>",
)
# https://docs.djangoproject.com/fr/2.2/ref/settings/#server-email
SERVER_EMAIL = getenv("DJANGO_SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)
# https://docs.djangoproject.com/fr/2.2/ref/settings/#email-subject-prefix
EMAIL_SUBJECT_PREFIX = getenv("DJANGO_EMAIL_SUBJECT_PREFIX", default="[El Géo Paso]")

# ADMIN
# ------------------------------------------------------------------------------
# Django Admin URL regex.
ADMIN_URL = getenv("DJANGO_ADMIN_URL")

# LOGGING
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/fr/2.2/ref/settings/#logging
# See https://docs.djangoproject.com/fr/2.2/topics/logging for
# more details on how to customize your logging configuration.
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "formatters": {"verbose": {"format": LOG_FORMAT}},  # noqa: F405
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {"level": "INFO", "handlers": ["console"]},
    "loggers": {
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },
        "django.security.DisallowedHost": {
            "level": "ERROR",
            "handlers": ["console", "mail_admins"],
            "propagate": True,
        },
    },
}
