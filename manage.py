# -*- coding: UTF-8 -*-
#! python3  # noqa: E265

"""Django's command-line utility for administrative tasks."""

# ############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging
import sys
from os import environ, path
from pathlib import Path

# 3rd party
from dotenv import find_dotenv, load_dotenv

# ############################################################################
# ########## Globals ###############
# ##################################

start_dir = Path(".")

# look for `.env` files
dotenv_files = list(start_dir.glob("*.env"))
if not len(dotenv_files):
    logging.info(
        "No environment ('.env') file found in: {}"
        " Using environment variables stored into the user and system levels.".format(
            start_dir.resolve()
        )
    )
elif len(dotenv_files) == 1:
    logging.info("Environment file found: {}".format(dotenv_files[0].resolve()))
    if dotenv_files[0].name == "example.env":
        logging.error(
            "Example environment file should not be used because it's git tracked."
        )
        raise
    # load environment variables
    load_dotenv(find_dotenv(dotenv_files[0]), override=True)
else:
    logging.warning(
        "Multiple ({}) environment files found. Picking one among: {}".format(
            len(dotenv_files), str(dotenv_files)
        )
    )
    for env_file in dotenv_files:
        if env_file.name == ".env":
            logging.info("Priority given to the pure '.env' file. Using it.")
            # load environment variables
            load_dotenv(env_file, override=True)
            break
        else:
            logging.warning(
                "No specific environment file found. Using the first: {}".format(
                    dotenv_files[0]
                )
            )
            # load environment variables
            load_dotenv(dotenv_files[0], override=True)


# ############################################################################
# ######### Functions ##############
# ##################################
def main():
    """Launch the Django's command-line utility for administrative tasks.

    :raises ImportError: if Django is not installed

    :example:

    .. code-block:: shell

        python manage.py --help
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
