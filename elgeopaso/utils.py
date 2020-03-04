# -*- coding: UTF-8 -*-
#! python3  # noqa: E265

"""Project utilities."""

# ############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging
from pathlib import Path

# 3rd party
from dotenv import find_dotenv, load_dotenv

# ############################################################################
# ######### Functions ##############
# ##################################


def find_and_load_environment_vars(start_dir: Path = "."):
    """Find and load environment files.

    :param Path start_dir: folder where to look for envi files. Defaults to: "." - optional

    :example:

    .. code-block:: python

        # here comes an example in Python
    """
    # look for `.env` files, ignoring example.env
    dotenv_files = [
        env_file
        for env_file in start_dir.glob("*.env")
        if env_file.name != "example.env"
    ]

    if not len(dotenv_files):
        logging.info(
            "No environment ('.env') file found in: {}"
            " Using environment variables stored into the user and system levels.".format(
                start_dir.resolve()
            )
        )
    elif len(dotenv_files) == 1:
        logging.info("Environment file found: {}".format(dotenv_files[0].resolve()))
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
