#! python3  # noqa: E265  # noqa E265

"""
Application in administration panel.
"""

# #############################################################################
# ########## Libraries #############
# ##################################

from django.contrib import admin

# Django
from django.db import models
from django.forms import Textarea, TextInput
from django.utils.html import format_html

# application
from elgeopaso.jobs.models import (
    Contract,
    ContractVariations,
    GeorezoRSS,
    JobPosition,
    JobPositionVariations,
    Offer,
    Place,
    PlaceVariations,
    Source,
    Technology,
    TechnologyVariations,
)


# #############################################################################
# ########### Classes ##############
# ##################################
# OFFERS
class OfferAdmin(admin.ModelAdmin):
    # FOREIGN KEY FIELDS
    def show_raw_offer(self, obj):
        return format_html(
            "<a href='/admin/jobs/georezorss/{rss_id}/change/'>"
            " Corriger l'offre {rss_id}</a>",
            rss_id=obj.id_rss,
        )

    show_raw_offer.short_description = "Offre brute"

    # FIELDS DISPLAY and FILTERS
    readonly_fields = (
        "content",
        "contract",
        "created",
        "jobs_positions",
        "place",
        "pub_date",
        "show_raw_offer",
        "source",
        "technologies",
        "title",
        "updated",
        "yearweek",
    )
    list_display = ("id_rss", "title", "short_content", "contract", "place", "pub_date")
    list_select_related = True
    list_filter = (
        "raw_offer__to_update",
        "pub_date",
        "contract",
        "technologies",
        "place",
    )
    search_fields = ("title", "content")
    date_hierarchy = "pub_date"
    ordering = ("-pub_date",)

    fieldsets = (
        ("Contenu", {"fields": ("title", "content")}),
        ("Date", {"fields": ("pub_date", "yearweek", "created", "updated")}),
        (
            "Informations extraites",
            {"fields": ("contract", "technologies", "place", "jobs_positions")},
        ),
        ("Autres", {"fields": ("show_raw_offer", "source")}),
    )


# TECHNOLOGIES
class TechnoVariationsInline(admin.TabularInline):
    list_display = ("name", "label")
    model = TechnologyVariations


class TechnologyAdmin(admin.ModelAdmin):
    readonly_fields = ("created", "updated")
    list_display = (
        "name",
        "license",
        "type_soft",
    )
    list_filter = ("name", "license", "type_soft")
    search_fields = ("name",)
    ordering = ("name",)
    inlines = (TechnoVariationsInline,)


class TechnologyVariationsAdmin(admin.ModelAdmin):
    list_display = ("label", "name")
    list_filter = ("name",)
    search_fields = ("label",)
    model = TechnologyVariations


# PLACES
class PlaceVariationsInline(admin.TabularInline):
    list_display = ("name", "label")
    model = PlaceVariations


class PlaceAdmin(admin.ModelAdmin):
    readonly_fields = ("created", "updated")
    list_display = ("name", "code", "scale")
    list_filter = ("scale",)
    search_fields = ("name", "code")
    ordering = ("code",)
    inlines = (PlaceVariationsInline,)


class PlaceVariationsAdmin(admin.ModelAdmin):
    list_display = ("label", "name")
    list_filter = ("name",)
    search_fields = ("label",)
    model = PlaceVariations


# JOBS POSITIONS
class JobPositionVariationsInline(admin.TabularInline):
    list_display = ("name", "label")
    model = JobPositionVariations


class JobPositionAdmin(admin.ModelAdmin):
    readonly_fields = ("created", "updated")
    list_display = ("name", "comment")
    list_filter = ("name",)
    search_fields = ("name",)
    inlines = (JobPositionVariationsInline,)


class JobPositionVariationsAdmin(admin.ModelAdmin):
    list_display = ("label", "name")
    list_filter = ("name",)
    search_fields = ("label",)
    model = JobPosition


# CONTRACT TYPES
class ContractVariationsInline(admin.TabularInline):
    list_display = ("name", "label")
    model = ContractVariations


class ContractsAdmin(admin.ModelAdmin):
    # FIELDS DISPLAY and FILTERS
    readonly_fields = ("created", "updated")
    list_display = ("abbrv", "name", "comment")
    list_filter = ("abbrv",)
    search_fields = ("name", "abbrv")
    ordering = ("abbrv",)
    inlines = (ContractVariationsInline,)


class ContractVariationsAdmin(admin.ModelAdmin):
    list_display = ("label", "name")
    list_filter = ("name",)
    search_fields = ("label",)
    model = ContractVariations


# SOURCES
class SourcesAdmin(admin.ModelAdmin):
    # FIELDS DISPLAY and FILTERS
    readonly_fields = ("created", "updated")
    list_display = ("name", "url", "comment")
    list_filter = ("name",)
    ordering = ("name",)


# GEOREZO
class GeorezoRSSAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField: {"widget": TextInput(attrs={"class": "span9"})},
        models.TextField: {"widget": Textarea(attrs={"class": "span9"})},
    }

    # LINK to clean offer
    def show_clean_offer(self, obj):
        return format_html(
            "<a href='/admin/jobs/offer/{offer_id}/change/'>"
            "Consulter l'offre traitée {offer_id}</a>",
            offer_id=obj.offre_traitee,
        )

    show_clean_offer.short_description = "Offre traitée"

    # ACTIONS
    def offers_to_update(self, request, queryset):
        rows_updated = queryset.update(to_update=1)
        if rows_updated == 1:
            message_bit = "1 offre a été"
        else:
            message_bit = "%s offres ont été" % rows_updated
        self.message_user(request, f"{message_bit} programmées à une nouvelle analyse.")

    offers_to_update.short_description = "Programmer une nouvelle analyse"

    actions = [offers_to_update]

    # Fields display management
    readonly_fields = (
        "created",
        "id_rss",
        "pub_date",
        "source",
        "updated",
        "show_clean_offer",
    )
    list_display = (
        "id_rss",
        "title",
        "short_content",
        "pub_date",
        "created",
        "updated",
    )
    list_display_links = ("id_rss", "title")
    list_filter = ("pub_date", "created", "updated", "to_update")
    list_select_related = True
    search_fields = ("title", "content")
    date_hierarchy = "pub_date"

    fieldsets = (
        ("Modifier", {"fields": ("title", "content", "to_update")}),
        ("Date", {"fields": ("pub_date", "created", "updated")}),
        ("Référence", {"fields": ("id_rss",)}),
        ("Autres", {"fields": ("source", "show_clean_offer")}),
    )


# #############################################################################
# ########## REGISTER ##############
# # ##################################
admin.site.register(Offer, OfferAdmin)
admin.site.register(Technology, TechnologyAdmin)
admin.site.register(TechnologyVariations, TechnologyVariationsAdmin)
admin.site.register(Place, PlaceAdmin)
admin.site.register(PlaceVariations, PlaceVariationsAdmin)
admin.site.register(JobPosition, JobPositionAdmin)
admin.site.register(JobPositionVariations, JobPositionVariationsAdmin)
admin.site.register(GeorezoRSS, GeorezoRSSAdmin)
admin.site.register(Contract, ContractsAdmin)
admin.site.register(ContractVariations, ContractVariationsAdmin)
admin.site.register(Source, SourcesAdmin)
