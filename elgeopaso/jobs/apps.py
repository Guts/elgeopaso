#! python3

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
