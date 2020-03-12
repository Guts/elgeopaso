# -*- coding: utf-8 -*-
#! python3  # noqa: E265

"""
    Settings built upon base for running tests.
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
# https://docs.djangoproject.com/fr/2.2/ref/settings/#secret-key
SECRET_KEY = getenv(
    "DJANGO_SECRET_KEY",
    default="xhaBNHx2NPM3H2xmvn7fV8puVuIYxKr2aODG3Iw1HNxbkKbwV6QtGM2OHiWNPD7f",
)

# https://docs.djangoproject.com/fr/2.2/ref/settings/#test-runner
TEST_RUNNER = "django.test.runner.DiscoverRunner"

# CACHES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/fr/2.2/ref/settings/#caches
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "tests-elgeopaso",
    }
}

# PASSWORDS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/fr/2.2/ref/settings/#password-hashers
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# TEMPLATES
# ------------------------------------------------------------------------------
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
# https://docs.djangoproject.com/fr/2.2/ref/settings/#email-backend
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
