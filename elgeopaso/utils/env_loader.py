#! python3  # noqa: E265

"""Project utilities."""

# ############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging
from os import getenv
from pathlib import Path

# 3rd party
from dotenv import find_dotenv, load_dotenv

# ############################################################################
# ######### Functions ##############
# ##################################


def find_and_load_environment_vars(start_dir: Path = "."):
    """Find and load environment files.

    :param Path start_dir: folder where to look for env files. Defaults to: "." - optional
    """
    # DOCKER
    USE_DOCKER = int(getenv("USE_DOCKER", default=0))

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
            if env_file.name == ".env" and not USE_DOCKER:
                logging.info("Priority given to the pure '.env' file. Using it.")
                # load environment variables
                load_dotenv(env_file, override=True)
                break
            elif env_file.name == "docker.env" and USE_DOCKER:
                logging.info(
                    "Docker enabled. Priority given to the 'docker.env' file. Using it."
                )
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
