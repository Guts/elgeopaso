#! python3  # noqa: E265

"""
Filters.

Learn more here: https://django-filter.readthedocs.io/en/master/
"""

# ###########################################################################
# ######### Libraries #############
# #################################

# standard library
# import logging

# Django
# from django.db import OperationalError

# django extensions
from django_filters import rest_framework as filters
from django_filters.widgets import BooleanWidget, RangeWidget

# Project
from elgeopaso.jobs.models import Offer


# #############################################################################
# ######### Filters ###############
# #################################
class OfferFilter(filters.FilterSet):
    """Filters related to search within offers."""

    # handle initial db migration which could consider that 'jobs_offer' is not existing
    # try:
    #     years = [i.year for i in Offer.objects.dates("pub_date", "year")]
    # except OperationalError as err:
    #     logging.error(
    #         "Error during filter construction. "
    #         "If it occured during initial migration, you can ignore it. "
    #         "Original error: {}".format(err)
    #     )
    #     years = []

    title = filters.CharFilter(lookup_expr="icontains", label="Le titre contient :")
    content = filters.CharFilter(lookup_expr="icontains", label="L'annonce contient :")
    date = filters.DateFromToRangeFilter(
        "pub_date",
        label="Publication",
        lookup_expr="contains",
        widget=RangeWidget(attrs={"placeholder": "DD/MM/YYYY"}),
    )

    raw_offer__to_update = filters.BooleanFilter(
        label="En attente", widget=BooleanWidget()
    )

    class Meta:
        model = Offer
        fields = [
            "contract",
            "place",
            "technologies",
            "pub_date",
            "content",
            "title",
            "raw_offer__to_update",
        ]
