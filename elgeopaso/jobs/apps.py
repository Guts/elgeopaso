#! python3  # noqa: E265  # noqa E265

"""
Application settings.
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Django
from django.apps import AppConfig

# #############################################################################
# ########### Classes ##############
# ##################################


class JobsConfig(AppConfig):
    name = "elgeopaso.jobs"
    verbose_name = "Offres d'emploi"
