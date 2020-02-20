# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Project URLs settings.

    Learn more here: https://docs.djangoproject.com/fr/2.2/topics/http/urls/
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Django
from django.urls import path
from django.views.generic import TemplateView

# project
from jobs import views

# #############################################################################
# ########### Globals ##############
# ##################################
app_name = "jobs"

urlpatterns = [
    path(r"", views.stats_home, name="index"),
    path(r"stats/", views.stats_contrats, name="stats"),
    path(r"timeline/", views.timeline, name="timeline"),
    path(r"search/", views.search, name="search"),
    path(r"map/", TemplateView.as_view(template_name="jobs/map.html"), name="map"),
    # Functions called via AJAX
    path(
        r"stats/get_offers_by_period",
        views.get_offers_by_period,
        name="get_offers_by_period",
    ),
    path(
        r"stats/get_types_contract_by_period",
        views.get_types_contract_by_period,
        name="get_types_contract_by_period",
    ),
    path(
        r"stats/get_contracts_by_technos",
        views.get_contracts_by_technos,
        name="get_contracts_by_technos",
    ),
    path(
        r"stats/get_countries_top5", views.get_countries_top5, name="get_countries_top5"
    ),
    path(r"stats/get_fr_dpts_top10", views.get_fr_dpts_top10, name="get_fr_dpts_top10"),
]
