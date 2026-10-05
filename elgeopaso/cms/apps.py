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
class CmsConfig(AppConfig):
    name = "elgeopaso.cms"
    verbose_name = "Contenu éditorial"
