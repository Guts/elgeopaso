# -*- coding: UTF-8 -*-
#! python3  # noqa: E265

"""Django's command-line utility for administrative tasks."""

# ############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import sys
from os import environ, path
from pathlib import Path

# modules
from elgeopaso import utils

# ############################################################################
# ########## Globals ###############
# ##################################

# find and load environment vars from .env file
utils.find_and_load_environment_vars(Path("."))


# ############################################################################
# ######### Functions ##############
# ##################################
def main():
    """Launch the Django's command-line utility for administrative tasks.

    :raises ImportError: if Django is not installed
    """
    # ensure that the Django project settings module to use is in the environment variables.
    # If not, it'll use the local settings by default
    environ.setdefault("DJANGO_SETTINGS_MODULE", "elgeopaso.settings.local")

    # then import Django CLI
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # This allows easy placement of apps within the interior project directory.
    current_path = path.dirname(path.abspath(__file__))
    sys.path.append(path.join(current_path, "elgeopaso"))

    # launch cli
    execute_from_command_line(sys.argv)


# ############################################################################
# ######## Stand-alone #############
# ##################################
if __name__ == "__main__":
    main()
