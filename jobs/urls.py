"""elpaso URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
#from django.conf.urls import url
from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = 'jobs'

urlpatterns = [
    path(r'', views.stats_home, name='index'),
    path(r'stats/', views.stats_contrats, name='stats'),
    path(r'timeline/', views.timeline, name='timeline'),
    path(r'search/', views.search, name='search'),
    path(r'map/', TemplateView.as_view(template_name='jobs/map.html'), name="map"),

    # Functions called via AJAX
    path(r'stats/get_offers_by_period',
         views.get_offers_by_period,
         name='get_offers_by_period'),

    path(r'stats/get_types_contract_by_period',
         views.get_types_contract_by_period,
         name='get_types_contract_by_period'),

    path(r'stats/get_contracts_by_technos',
         views.get_contracts_by_technos,
         name='get_contracts_by_technos'),

    path(r'stats/get_countries_top5',
         views.get_countries_top5,
         name='get_countries_top5'),

    path(r'stats/get_fr_dpts_top10',
         views.get_fr_dpts_top10,
         name='get_fr_dpts_top10'),
]
