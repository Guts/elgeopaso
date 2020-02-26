# -*- coding: UTF-8 -*-
#! python3  # noqa: E265  # noqa E265

# ###########################################################################
# ######### Libraries #############
# #################################

# Standard library
import logging
import json

# Django
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.views.decorators.gzip import gzip_page
from django.views.decorators.http import require_safe

# project
from .filters import OfferFilter
from .models import Offer, Contract
from cms.models import Article
from .decorators import conditional_cache

# 3rd party modules
import arrow

# ############################################################################
# ########## Globals ##############
# #################################

utc = arrow.utcnow()

# #############################################################################
# ########## Views ################
# #################################


@require_safe
@gzip_page
@cache_page(60 * 60)  # in seconds
def stats_home(request):
    """Displays global metrics about database on homepage."""
    # KPIs
    nb_offers = Offer.objects.count()

    if nb_offers:
        last_date = Offer.objects.latest("pub_date").pub_date
        first_date = Offer.objects.earliest("pub_date").pub_date
    else:
        logging.warning("No offers in the database.")
        last_date = first_date = ""

    # content
    # presentation = Article.objects.get(slug_title="homepage-presentation")
    presentation = "Héhé"

    # values to replace within the template
    context = {
        "nb_contrats": nb_offers,
        "first_date": first_date,
        "last_date": last_date,
        "presentation": presentation,
    }

    # function end
    return render(request, "jobs/home.html", context)


@require_safe
@gzip_page
@cache_page(60 * 60)
def stats_contrats(request):
    """Renders statistics by contracts type on contracts page."""
    # global KPIs
    nb_offers = Offer.objects.count()
    if nb_offers:
        nb_place_all = Offer.objects.exclude(place="ND").count()
        nb_contract_all = Offer.objects.exclude(contract="ND").count()
        nb_place_perc = int(100 * nb_place_all / nb_offers)
        nb_contract_perc = int(100 * nb_contract_all / nb_offers)
        week_actual_year = Offer.objects.filter(
            week="{}{}".format(*utc.shift(weeks=-1).isocalendar()[0:2])
        ).count()
        week_last_year = Offer.objects.filter(
            week="{}{}".format(*utc.shift(weeks=-1, years=-1).isocalendar()[0:2])
        ).count()
        week_comparison_perc = round(
            (week_actual_year - week_last_year) / week_last_year * 100, 2
        )
    else:
        logging.warning("No offers in the database.")
        nb_contract_perc = nb_place_perc = week_comparison_perc = 0

    # stats par types de contrat
    contracts_types = [
        {"x": "CDI", "y": Offer.objects.filter(contract="CDI").count()},
        {"x": "CDD", "y": Offer.objects.filter(contract="CDD").count()},
        {"x": "FPT/FPE", "y": Offer.objects.filter(contract="FP E/T").count()},
        {"x": "Interim", "y": Offer.objects.filter(contract="Intérim").count()},
        {"x": "Stages", "y": Offer.objects.filter(contract="Stage").count()},
        {
            "x": "Apprentissage",
            "y": Offer.objects.filter(contract="Alternance").count(),
        },
        {
            "x": "Recherche",
            "y": Offer.objects.filter(contract="Thèse").count()
            + Offer.objects.filter(contract="Postdoctorat").count(),
        },
        {
            "x": "Autres",
            "y": Offer.objects.filter(contract="Expatriation").count()
            + Offer.objects.filter(contract="Autres").count()
            + Offer.objects.filter(contract="Volontariat").count(),
        },
        {"x": "Non reconnu", "y": Offer.objects.filter(contract="ND").count()},
    ]

    # values to replace within the template
    context = {
        "global_kpi": [
            nb_offers,
            nb_contract_perc,
            nb_place_perc,
            week_comparison_perc,
        ],
        "contracts_types": contracts_types,
    }

    # function end
    return render(request, "jobs/stats.html", context)


@require_safe
@gzip_page
@cache_page(60 * 60)
def get_offers_by_period(request):
    """
    Get the number of offers per
    period (year, month, week).
    month and week TO DO
    Called via AJAX
    """
    period = request.GET["period"]
    if period == "year":
        years = [i.year for i in Offer.objects.dates("pub_date", "year")]

        offers = [
            {
                "values": [
                    {"x": year, "y": Offer.objects.filter(pub_date__year=year).count()}
                    for year in years
                ],
                "key": "Offres",
                "color": "#decbe4",
            }
        ]
    elif period == "month":
        months = [i.month for i in Offer.objects.dates("pub_date", "month")]
        pass
    # weeks
    else:
        pass

    return HttpResponse(json.dumps(offers))


@require_safe
@gzip_page
@cache_page(60 * 60)
def get_types_contract_by_period(request):
    """
    Get the number types of contract per
    period (year, month, week).
    month and week TO DO
    Called via AJAX
    """
    conts_abbrvs = list(
        Contract.objects.exclude(abbrv__in=["Autres", "Expatriation", "ND"])
        .values_list("abbrv", flat=True)
        .order_by("abbrv")
    )
    colors = (
        "#8dd3c7",
        "#fdb462",
        "#fb8072",
        "#80b1d3",
        "#bebada",
        "#b3de69",
        "#fccde5",
        "#d9d9d9",
        "#fccde5",
        "#bc80bd",
    )

    period = request.GET["period"]

    if period == "year":
        years = [i.year for i in Offer.objects.dates("pub_date", "year")]

        cts_years = []

        for ct in conts_abbrvs:
            cts_years.append(
                {
                    "color": colors[conts_abbrvs.index(ct)],
                    "key": ct,
                    "values": [
                        (y, Offer.objects.filter(contract=ct, pub_date__year=y).count())
                        for y in years
                    ],
                }
            )

    elif period == "month":
        pass
    # weeks
    else:
        pass

    return HttpResponse(json.dumps(cts_years))


@require_safe
@gzip_page
@cache_page(60 * 60)
def get_contracts_by_technos(request):
    """Count offers by contracts types and software passed."""
    # req = request.GET
    # softs = req.getlist("softs[]")
    # cts = req.getlist("contracts[]")
    # logging.debug(softs, cts)

    # variables from models
    years = [i.year for i in Offer.objects.dates("pub_date", "year")]
    tech_top5 = (
        Offer.objects.values("technologies__name")
        .annotate(offers_count=Count("technologies"))
        .order_by("-offers_count")[:5]
    )

    cts_tech = []
    for tek in tech_top5:
        tek_name = tek.get("technologies__name")
        # tek_count = tek.get("offers_count")
        cts_tech.append(
            {
                "key": tek_name,
                # "key": "{} ({})".format(tek_name, tek_count),
                "values": [
                    (
                        y,
                        Offer.objects.select_related()
                        .filter(
                            technologies__name=tek_name,
                            # contract="CDI",
                            pub_date__year=y,
                        )
                        .count(),
                    )
                    for y in years
                ],
            }
        )

    # MEMO - DATA STRCTURE EXPECTED
    # cts_tech = [{"key": "QGIS",
    #              "values": [("2015", "132"), ("2016", "150"), ("2017", "200")],
    #              "color": '#2ca02c'},
    #             {"key": "Esri",
    #              "values": [("2015", "200"), ("2016", "185"), ("2017", "135")],
    #              "color": '#7777ff'}]
    # logging.debug(cts_tech)
    # print(type(cts_tech))
    return HttpResponse(json.dumps(cts_tech))


@require_safe
@gzip_page
@cache_page(60 * 60)
def get_fr_dpts_top10(request):
    """Count offers by French departments, including DOM TOM."""
    qdpt = Q(place__scale="DEPARTEMENT")
    qtom = Q(place__scale="TOM")
    dtps_toms = Offer.objects.filter(qdpt | qtom)
    # variables from models
    dpts_toms_top10 = (
        dtps_toms.values("place__name").annotate(y=Count("place")).order_by("-y")[:10]
    )
    dpts_toms_others = dtps_toms.exclude(
        place__code__in=dpts_toms_top10.values_list("place__code", flat=True)
    )

    ct_dpts_toms = [
        {"x": "Autres", "y": dpts_toms_others.count()},
    ]
    for i in dpts_toms_top10:
        ct_dpts_toms.append({"x": i.get("place__name"), "y": i.get("y")})
    return HttpResponse(json.dumps(ct_dpts_toms))


@require_safe
@gzip_page
@cache_page(60 * 60)
def get_countries_top5(request):
    """Count offers by countries other than France."""
    # variables from models
    countries = Offer.objects.exclude(place__code="FRA").filter(place__scale="COUNTRY")
    countries_top5 = (
        countries.values("place__name").annotate(y=Count("place")).order_by("-y")[:5]
    )
    countries_others = countries.exclude(
        place__code__in=countries_top5.values_list("place__code", flat=True)
    )

    ct_countries = [
        {"x": "Autres", "y": countries_others.count()},
    ]
    for i in countries_top5:
        ct_countries.append({"x": i.get("place__name"), "y": i.get("y")})
    return HttpResponse(json.dumps(ct_countries))


# ----------------------------------------------------------------------------


@require_safe
@gzip_page
@cache_page(60 * 60)
def timeline(request):
    """Displays 50 latest offers."""
    dico_styles = {
        "Alternance": ("far fa-star-half", "primary disabled"),
        "Autres": ("fas fa-question", "default"),
        "CDI": ("fas fa-star", "success"),
        "CDD": ("far fa-star", "info"),
        "Expatriation": ("far fa-paper-plane", "info"),
        "FP E/T": ("fas fa-university", "success"),
        "Intérim": ("fas fa-history", "default"),
        "ND": ("fas fa-question", "disabled"),
        "Postdoctorat": ("fas fa-graduation-cap", "warning"),
        "Stage": ("fas fa-child", "primary disabled"),
        "Thèse": ("fas fa-graduation-cap", "warning"),
        "Volontariat": ("far fa-paper-plane", "info"),
    }

    last50 = Offer.objects.order_by("-pub_date")[:50]

    top50 = [
        {
            "title": i.title,
            "contract": i.contract.abbrv,
            "description": i.short_content,
            "date": i.pub_date,
            "delay": arrow.get(i.pub_date).humanize(locale="FR_fr"),
            "badge": dico_styles.get(i.contract.abbrv, "Stage")[0],
            "id_rss": i.id_rss,
            "kind": dico_styles.get(i.contract.abbrv, "Stage")[1],
            "link": "https://georezo.net/forum/viewtopic.php?pid={}".format(i.id_rss),
            "technos": i.technologies.values("name", "license", "type_soft"),
            "place": i.place.name,
            "jobs": i.jobs_positions.values("name"),
            "osm": "https://www.openstreetmap.org/search?query={}".format(i.place.name),
        }
        for i in last50
    ]

    # function end
    return render(request, "jobs/timeline.html", {"last50": top50})


# ----------------------------------------------------------------------------


@require_safe
@gzip_page
@conditional_cache(decorator=cache_page(60 * 60))
def search(request):
    """Search form."""
    offers_qs = Offer.objects.select_related().all()
    offers_filtered = OfferFilter(request.GET, queryset=offers_qs)
    paginator = Paginator(offers_filtered.qs, 25)

    page = request.GET.get("page")
    try:
        offer_filter = paginator.page(page)
    except PageNotAnInteger:
        offer_filter = paginator.page(1)
    except EmptyPage:
        offer_filter = paginator.page(paginator.num_pages)

    return render(
        request, "jobs/search.html", {"offers": offer_filter, "filter": offers_filtered}
    )
