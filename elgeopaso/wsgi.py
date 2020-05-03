"""
    WSGI config for elgeopaso project.

    It exposes the WSGI callable as a module-level variable named ``application``.

    For more information on this file, see
    https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

# Standard library
import logging
import sys
from os import environ, getenv
from pathlib import Path

# Django
from django.core.wsgi import get_wsgi_application  # noqa: E402

# modules
from elgeopaso.utils.env_loader import find_and_load_environment_vars

# ############################################################################
# ########## Globals ###############
# ##################################


# This allows easy placement of apps within the interior
# django_starter directory.
APP_DIR_PATH = Path(__file__).parents[2].resolve() / getenv(
    "DJANGO_PROJECT_FOLDER", default="elgeopaso"
)
# APP_DIR_PATH = os.path.abspath(
#     os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)
# )
sys.path.append(str(APP_DIR_PATH.resolve()))  # must be a string
logging.warning("Application path added to the PATH: {}".format(APP_DIR_PATH))

# find and load environment vars from .env file
find_and_load_environment_vars(APP_DIR_PATH)

# We defer to a DJANGO_SETTINGS_MODULE already in the environment. This breaks
# if running multiple sites in the same mod_wsgi process. To fix this, use
# mod_wsgi daemon mode with each site in its own daemon process.
# environ["DJANGO_SETTINGS_MODULE"] = "elgeopaso.settings.production"
environ.setdefault("DJANGO_SETTINGS_MODULE", "elgeopaso.settings.production")

# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.
application = get_wsgi_application()

# Apply WSGI middleware here. Example:
# from helloworld.wsgi import HelloWorldApplication
# application = HelloWorldApplication(application)
