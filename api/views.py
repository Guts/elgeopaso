# -*- coding: utf-8 -*-
#!/usr/bin/env python

# ###########################################################################
# ######### Libraries #############
# #################################
# Standard library

# Django

# PROJECT APPS
from jobs.models import Contract, JobPosition, Offer, Place, PlaceVariations, Technology
from api.serializers import (
    ContractSerializer,
    JobSerializer,
    PlaceSerializer,
    PlaceVariationsSerializer,
    OfferSerializer,
    TechnoSerializer,
)

# REST API
from rest_framework import generics, viewsets
from django_filters import rest_framework as filters

# #############################################################################
# ########## Views ################
# #################################


class ContractViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows contracts types to be viewed or edited.
    """

    queryset = Contract.objects.all().order_by("abbrv")
    serializer_class = ContractSerializer


class JobViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows contracts types to be viewed or edited.
    """

    queryset = JobPosition.objects.all().order_by("name")
    serializer_class = JobSerializer


class OfferViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows offers to be viewed or edited.
    """

    queryset = (
        Offer.objects.select_related("contract", "place", "raw_offer")
        .all()
        .order_by("pub_date")
    )

    serializer_class = OfferSerializer


class PlaceVariationsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Places used as reference to parse raw offers.
    """

    queryset = PlaceVariations.objects.all()
    serializer_class = PlaceVariationsSerializer


class PlaceViewSet(viewsets.ModelViewSet):
    """
    Places used as reference to parse raw offers.
    """

    queryset = Place.objects.all()
    serializer_class = PlaceSerializer


class TechnoViewSet(viewsets.ModelViewSet):
    """
    Places used as reference to parse raw offers.
    """

    queryset = Technology.objects.all()
    serializer_class = TechnoSerializer
