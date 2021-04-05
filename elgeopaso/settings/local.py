#! python3  # noqa: E265

"""
    Settings built upon base for local development.
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
from os import getenv

# common settings
from .base import *  # noqa

# ##############################################################################
# ########## Globals ###############
# ##################################
# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/fr/2.2/ref/settings/#debug
DEBUG = True
# https://docs.djangoproject.com/fr/2.2/ref/settings/#secret-key
SECRET_KEY = getenv(
    "DJANGO_SECRET_KEY",
    default="xhaBNHx2NPM3H2xmvn7fV8puVuIYxKr2aODG3Iw1HNxbkKbwV6QtGM2OHiWNPD7f",
)

# https://docs.djangoproject.com/fr/2.2/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1"]

# CACHES
# https://docs.djangoproject.com/fr/2.2/topics/cache/
# https://docs.djangoproject.com/fr/2.2/ref/settings/#caches
# ------------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-elgeopaso",
    }
}

# APPS
# https://docs.djangoproject.com/fr/2.2/ref/settings/#installed-apps
# ------------------------------------------------------------------------------
DEVELOPMENT_APPS = ["debug_toolbar", "django_extensions"]
INSTALLED_APPS += DEVELOPMENT_APPS  # noqa: F405

# For development, Whitenoise must be added at the top of installed apps
# http://whitenoise.evans.io/en/latest/django.html#using-whitenoise-in-development
INSTALLED_APPS = ["whitenoise.runserver_nostatic"] + INSTALLED_APPS  # noqa F405


# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/fr/2.2/ref/settings/#email-backend
EMAIL_BACKEND = getenv(
    "DJANGO_EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)


# django-debug-toolbar
# ------------------------------------------------------------------------------
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#prerequisites
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#middleware
MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]  # noqa F405
# https://django-debug-toolbar.readthedocs.io/en/latest/configuration.html#debug-toolbar-config
DEBUG_TOOLBAR_CONFIG = {
    "DISABLE_PANELS": ["debug_toolbar.panels.redirects.RedirectsPanel"],
    "SHOW_TEMPLATE_CONTEXT": True,
}
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#internal-ips
INTERNAL_IPS = ["127.0.0.1", "10.0.2.2"]

# Adaptations for Docker usage
if int(getenv("USE_DOCKER", default=0)):
    import socket

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS += [ip[:-1] + "1" for ip in ips]
