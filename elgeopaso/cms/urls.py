#! python3  # noqa: E265  # noqa E265

"""
Application URLs settings.
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Django
from django.conf.urls import url

from elgeopaso.cms import views

# #############################################################################
# ########### Globals ##############
# ##################################
urlpatterns = [
    url(r"^about/$", views.about, name="about"),
    url(r"^(?P<slug>[-\w]+)/$", views.view_category, name="view_category"),
    url(
        r"^(?P<category>[-\w]+)/(?P<slug>[-\w]+)/$",
        views.view_article,
        name="view_article",
    ),
]
