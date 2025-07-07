#! python3  # noqa: E265  # noqa E265

"""
Project URLs settings.

Learn more here: https://docs.djangoproject.com/fr/2.2/topics/http/urls/

To add a new path:

.. code-block:: python

    # first import the app
    import jobs

    # then add the new path:
    path('jobs/', jobs.urls, name="Jobs offers")

"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Django
from django.conf import settings
from django.contrib import admin
from django.urls import include, path

# #############################################################################
# ########### Globals ##############
# ##################################
admin.autodiscover()


# List of accepted URLs
urlpatterns = [
    # administration panel
    path("admin/", admin.site.urls),
    # authentication flow
    path("accounts/", include("allauth.urls")),
    # Jobs analytics
    path("", include("elgeopaso.jobs.urls", "index"), name="home"),
    path("jobs/", include("elgeopaso.jobs.urls")),
    # CMS
    path("content/", include(("elgeopaso.cms.urls", "cms"), namespace="cms")),
    path("ckeditor/", include("ckeditor_uploader.urls")),
    # API
    path("api/", include(("elgeopaso.api.urls", "api"), namespace="api")),
]


# Addtionnal configuration for local development
if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    # urlpatterns += [
    #     path(
    #         "400/",
    #         default_views.bad_request,
    #         kwargs={"exception": Exception("Bad Request!")},
    #     ),
    #     path(
    #         "403/",
    #         default_views.permission_denied,
    #         kwargs={"exception": Exception("Permission Denied")},
    #     ),
    #     path(
    #         "404/",
    #         default_views.page_not_found,
    #         kwargs={"exception": Exception("Page not Found")},
    #     ),
    #     path("500/", default_views.server_error),
    # ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
