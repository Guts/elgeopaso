from django.contrib.sitemaps import Sitemap

from cms.models import Article


class ArticleSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return Article.objects.filter(published=True)

    def lastmod(self, obj):
        return obj.updated
