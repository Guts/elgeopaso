# -*- coding: utf-8 -*-
#! python3  # noqa: E265

# ############################################################################
# ########## Libraries #############
# ##################################
# Standard library
import json
from os import path

# Django
from django.conf import settings
from django.core.management.base import BaseCommand
from django.templatetags.static import static

# Django project
from jobs.models import Offer


# ############################################################################
# ########### Classes #############
# #################################


class Command(BaseCommand):
    args = "<foo bar ...>"
    help = """
                Commands to generate geojson files used for map visualization.
                GeoJSON are downloaded from:
                https://github.com/gregoiredavid/france-geojson
           """

    # Parsing options ------------------------------------------------------

    # def add_arguments(self, parser):
    #     # Positional arguments
    #     parser.add_argument('poll_id', nargs='+', type=int)
    #     parser.add_argument('poll_id', nargs='+', type=int)

    #     # Named (optional) arguments
    #     parser.add_argument(
    #         '--delete',
    #         action='store_true',
    #         dest='delete',
    #         default=False,
    #         help='Delete poll instead of closing it',
    #     )

    def handle(self, *args, **options):
        """Parse input GeoJSON and update needed values to display maps."""
        # vars
        years = [i.year for i in Offer.objects.dates("pub_date", "year")]
        # load input geojson
        in_gjson_metro = path.normpath(
            str(settings.ROOT_DIR) + static("jobs/geojson/dpts_metro.json")
        )
        with open(in_gjson_metro) as data_file:
            data = json.load(data_file)

        # prepare metrics
        offers_dpts = Offer.objects.filter(place__scale__exact="DEPARTEMENT")

        # parsing
        for feat in data.get("features"):
            props = feat.get("properties")
            dpt_offers = offers_dpts.filter(place__code=props.get("CODE_DEPT"))
            props["JOBS_TOTAL"] = dpt_offers.count()
            for y in years:
                props["JOBS_{}".format(y)] = dpt_offers.filter(pub_date__year=y).count()
                props["histo"] = [
                    {
                        "values": [
                            {
                                "x": year,
                                "y": dpt_offers.filter(pub_date__year=year).count(),
                            }
                            for year in years
                        ],
                        "key": "Offres",
                        "color": "#decbe4",
                    }
                ]
        # Save file
        out_gjson_metro = path.normpath(
            str(settings.ROOT_DIR) + "/assets/jobs/geojson/dpts_metro_jobs.json"
        )
        with open(out_gjson_metro, "w") as jsonFile:
            json.dump(data, jsonFile)
