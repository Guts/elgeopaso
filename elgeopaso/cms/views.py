from django.shortcuts import get_object_or_404, render, render_to_response
from django.views import generic
from django.views.decorators.cache import cache_page
from django.views.decorators.gzip import gzip_page
from django.views.decorators.http import require_safe

from elgeopaso.cms.models import Article, Category


# @require_safe
# @gzip_page
# @cache_page(60 * 60)
# def about(request):
#     """Displays global metrics about database on homepage."""
#     content = Article.objects.filter(published=1).first().content

#     # values to replace within the template
#     context = {
#         "content": content,
#     }

#     # function end
#     return render(request, "cms/about.html", context)


# @require_safe
# @gzip_page
# @cache_page(60 * 60)
# def docs(request):
#     """Documentation content."""
#     docs_list = Article.objects.filter(category="Documentation", published=1)

#     return render(request, "cms/documentation.html", {"filter": docs_list})


# @require_safe
# @gzip_page
# @cache_page(60 * 60)
# def view_category(request, slug):
#     category = get_object_or_404(Category, slug_name=slug)
#     return render_to_response(
#         "cms/category_detail.html",
#         {
#             "categories": Category.objects.all(),
#             "category": category,
#             "articles": Article.objects.filter(
#                 published=True, category=category
#             ).order_by("-updated")[:5],
#         },
#     )


# @require_safe
# @gzip_page
# @cache_page(60 * 60)
# def view_article(request, slug, category):
#     return render_to_response(
#         "cms/article_detail.html",
#         {"article": get_object_or_404(Article, slug_title=slug)},
#     )


class ArticleDetail(generic.DetailView):
    model = Article
    template_name = "cms/article_detail.html"


class ArticleList(generic.ListView):
    queryset = Article.objects.all()
    template_name = "cms/index.html"
    paginate_by = 3
