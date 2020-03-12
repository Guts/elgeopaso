# -*- coding: UTF-8 -*-
#! python3  # noqa: E265

"""
    Application views.

    Learn more here: https://docs.djangoproject.com/fr/2.2/topics/http/views/
"""

# ###########################################################################
# ######### Libraries #############
# #################################

# Standard library
import logging
import time

# Django
from django import template
from django.conf import settings

# ###########################################################################
# ########## Globals ##############
# #################################
register = template.Library()

# ###########################################################################
# ####### Template tags ###########
# #################################
@register.simple_tag
def version_date(date_format: str = "%d/%m/%Y") -> str:
    """Return the last modification date based on git. \
        If git folder does not exist, an empty string is returned instead.

    :return: last modification date
    :rtype: str

    :example:

    .. code-block:: html

        # from a Django template, first load the custom templatetag
        {% load version %}

        # in a text div
        <p>
          My awesome project - Last updated: {% version_date %}
        </p>

    """
    git_folder = settings.ROOT_DIR / ".git"
    if git_folder.exists():
        logging.debug("Git folder found")
        return time.strftime(date_format, time.gmtime(git_folder.stat().st_mtime))
    else:
        return ""


@register.simple_tag
def version_number() -> str:
    """Return the project version as number.

    :return: version number
    :rtype: str

    :example:

    .. code-block:: html

        # from a Django template, first load the custom templatetag
        {% load version %}

        # in a text div
        <p>
          My awesome project - version {% version_number %}
        </p>

    """
    return settings.PROJECT_VERSION
