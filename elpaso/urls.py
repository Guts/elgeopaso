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
from django.conf import settings
#from django.conf.urls import include, url
from django.urls import include, path
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap

# sitemaps
from .sitemaps import StaticViewSitemap
from cms.sitemaps import ArticleSitemap

# URLs
urlpatterns = [
    # admin
    path('admin/', admin.site.urls),

    path(r'', include("jobs.urls", "index")),
    # Jobs analytics
    path('jobs/', include("jobs.urls")),

    # CMS
    path('content/', include(("cms.urls", "cms"), namespace='cms')),
    path('ckeditor/', include('ckeditor_uploader.urls')),

    # API
    path('api/', include(("api.urls", "api"), namespace='api')),
    ]

# SITEMAPS
sitemaps = {"pages": StaticViewSitemap,
            "articles": ArticleSitemap,
           }
urlpatterns.append(path('sitemap.xml',
                        sitemap,
                        {'sitemaps': sitemaps},
                        name='django.contrib.sitemaps.views.sitemap'
                       )
                  )

# DEV MODE
if settings.DEBUG:
    # DTB
    import debug_toolbar
    urlpatterns.append(path('__debug__/', include(debug_toolbar.urls)))
    # MEDIA
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
