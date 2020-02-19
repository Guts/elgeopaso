# -*- coding: UTF-8 -*-
#! python3  # noqa E265

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
    name = "jobs"
    verbose_name = "Offres d'emploi en géomatique francophone"