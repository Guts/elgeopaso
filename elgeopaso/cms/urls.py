#! python3  # noqa: E265  # noqa E265

"""
Application URLs settings.
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Django
from django.urls import path

from elgeopaso.cms import views

# #############################################################################
# ########### Globals ##############
# ##################################
urlpatterns = [
    path("about/", views.about, name="about"),
    path("<slug:slug>/", views.view_category, name="view_category"),
#    re_path(r"^(?P<slug>[-\w]+)/$", views.view_category, name="view_category"),
#    path(r"^(?P<slug>[-\w]+)/$", views.view_category, name="view_category"),
    path("<slug:category>/<slug:slug>/", views.view_article, name="view_article"),
#    re_path(r"^(?P<category>[-\w]+)/(?P<slug>[-\w]+)/$", views.view_article, name="view_article"),
#    path(
#        r"^(?P<category>[-\w]+)/(?P<slug>[-\w]+)/$",
#        views.view_article,
#        name="view_article",
#    ),
]
