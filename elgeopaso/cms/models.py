# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.core.validators import MaxLengthValidator
from django.db import models
from django.template.defaultfilters import truncatechars
from django.urls import reverse

# 3rd party package
from ckeditor_uploader.fields import RichTextUploadingField

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Catégorie")
    slug_name = models.SlugField(verbose_name="Alias normé", unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name="Description")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("view_category", kwargs={"slug": self.slug_name})

    class Meta:
        app_label = "cms"
        ordering = ["name"]
        verbose_name = "Type de contenu"
        verbose_name_plural = "Types de contenu"


class Article(models.Model):
    # meta
    author = models.ForeignKey(
        User, verbose_name="Auteur.e", null=True, on_delete=models.SET_NULL
    )
    category = models.ForeignKey(
        Category, verbose_name="Catégorie", null=True, on_delete=models.SET_NULL
    )
    # content
    title = models.CharField(
        "Titre", max_length=200, validators=[MaxLengthValidator(200)]
    )
    slug_title = models.SlugField(verbose_name="Alias normé", unique=True, blank=True)
    content = RichTextUploadingField("Corps de texte")
    ext_url = models.URLField("Lien externe", blank=True)
    published = models.BooleanField("Publié", blank=False, default=False)
    # dates
    created = models.DateTimeField("Créé le", auto_now_add=True)
    updated = models.DateTimeField("Modifié le", auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            "cms:view_article",
            kwargs={"slug": self.slug_title, "category": self.category.slug_name},
        )
        # return "/content/{}/{}".format(self.category.slug_name, self.slug_title)

    @property
    def short_content(self):
        return truncatechars(self.content, 300)

    class Meta:
        app_label = "cms"
        get_latest_by = "updated"
        ordering = [
            "title",
        ]
        verbose_name = "Contenu éditorial"
        verbose_name_plural = "Contenus éditoriaux"
