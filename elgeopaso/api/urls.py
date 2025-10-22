#! python3  # noqa: E265  # noqa E265

"""
Application URLs settings.

Learn more here:

- https://docs.djangoproject.com/fr/2.2/topics/http/urls/
- https://docs.djangoproject.com/fr/2.2/ref/urls/
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Django
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

# Dajngo REST Framework
from rest_framework import routers

# application
from elgeopaso.api import views

# #############################################################################
# ########### Globals ##############
# ##################################

# API ROUTING
router = routers.SimpleRouter()

router.register(r"contrats", views.ContractViewSet)
router.register(r"lieux", views.PlaceViewSet)
router.register(r"lieux_variantes", views.PlaceVariationsViewSet)
router.register(r"offres", views.OfferViewSet)
router.register(r"metiers", views.JobViewSet)
router.register(r"technos", views.TechnoViewSet)

urlpatterns = [
    path("schema/", SpectacularAPIView.as_view(api_version="api/1.0"), name="schema"),
    path(
        "docs/",
        SpectacularSwaggerView.as_view(url_name="api:schema"),
        name="swagger-ui",
    ),
    path("redoc/", SpectacularRedocView.as_view(url_name="api:schema"), name="redoc"),
    path("", include(router.urls)),
]
