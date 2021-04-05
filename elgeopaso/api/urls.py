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
from django.conf import settings
from django.urls import re_path

# Dajngo REST Framework
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions, routers

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

urlpatterns = router.urls

# API SWAGGER
schema_view = get_schema_view(
    openapi.Info(
        title="El Géo Paso - Documentation de l'API",
        default_version="v1",
        description="Documentation standardisée de l'API REST d'El Géo Paso",
        terms_of_service="https://blog.georezo.net/laminute/tout-sur-georezo/mentions-legales/",
        contact=openapi.Contact(email=settings.EMAIL_HOST_USER),
    ),
    public=False,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns += [
    # OpenAPI files
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=60 * 60),
        name="schema-json",
    ),
    # Swagger UI
    re_path(
        "swagger|docs",
        schema_view.with_ui(renderer="swagger", cache_timeout=60 * 60),
        name="schema-swagger-ui",
    ),
]
