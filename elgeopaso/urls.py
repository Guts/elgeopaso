from django.conf import settings
from django.urls import include, path

from django.contrib import admin

admin.autodiscover()

import jobs.views

# To add a new path, first import the app:
# import blog
#
# Then add the new path:
# path('blog/', blog.urls, name="blog")
#
# Learn more here: https://docs.djangoproject.com/en/2.1/topics/http/urls/

urlpatterns = [
    path("", jobs.views.index, name="index"),
    path("db/", jobs.views.db, name="db"),
    path("admin/", admin.site.urls),
    # CMS
    path("content/", include(("cms.urls", "cms"), namespace="cms")),
    path("ckeditor/", include("ckeditor_uploader.urls")),
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
