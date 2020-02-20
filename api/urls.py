from django.urls import path
from rest_framework import routers
from rest_framework_swagger.views import get_swagger_view
from api import views

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
schema_view = get_swagger_view(title="El Géo Paso - API", url="/")
urlpatterns.append(path(r"docs", schema_view, name="API_Documentation"))
