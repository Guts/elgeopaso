# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import Article, Category


class ArticleAdmin(admin.ModelAdmin):
    # FIELDS DISPLAY and FILTERS
    list_display = ("title", "slug_title", "category", "created", "updated")
    list_filter = ("category", "author", "published")
    prepopulated_fields = {"slug_title": ("title",)}
    search_fields = ("title", "content")
    ordering = ("created",)

    fieldsets = (
        ("Métadonnées", {"fields": ("category", "author",)}),
        ("Titre", {"fields": ("title", "slug_title",)}),
        ("Contenu", {"classes": ("full-width",), "fields": ("content",)}),
        ("Divers", {"fields": ("ext_url",)}),
        ("Publication", {"fields": ("published",)}),
    )


class CategoryAdmin(admin.ModelAdmin):
    # FIELDS DISPLAY and FILTERS
    list_display = ("name", "slug_name", "description")
    list_filter = ("name",)
    prepopulated_fields = {"slug_name": ("name",)}
    ordering = ("name",)
    search_fields = ("name", "description")


# REGISTERING and DISPLAY
admin.site.register(Article, ArticleAdmin)
admin.site.register(Category, CategoryAdmin)
