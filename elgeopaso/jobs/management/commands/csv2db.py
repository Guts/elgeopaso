#! python3  # noqa: E265

"""
    Command used to import a CSV from a Georezo database export.

    .. code-block:: python

        python manage.py csv2db --input-csv ./georezo/georezo_db_backup_2016-2017.csv

"""

import csv
import logging

# #############################################################################
# ######### Libraries #############
# #################################
# Standard library
from argparse import RawTextHelpFormatter
from os import path

# 3rd party modules
import arrow

# Django project
from django.core.management.base import BaseCommand

from elgeopaso.jobs.models import GeorezoRSS

# ############################################################################
# ########## Globals #############
# ################################

csv.register_dialect(
    "pipe",
    delimiter="|",
    escapechar="\\",
    skipinitialspace=1,
    quotechar='"',
    doublequote=True,
)

# ############################################################################
# ########## Classes #############
# ################################


class Command(BaseCommand):
    args = "<foo bar ...>"
    help = """
              Import CSV data into the project database
           """.strip()

    # Parsing options ------------------------------------------------------
    def create_parser(self, *args, **kwargs):
        parser = super(Command, self).create_parser(*args, **kwargs)
        parser.formatter_class = RawTextHelpFormatter
        return parser

    def add_arguments(self, parser):
        parser.add_argument(
            "--input-csv",
            nargs="?",
            type=str,
            dest="input-csv",
            default=None,
            help="Path to the input CSV.",
        )

    def handle(self, *args, **options):
        if options.get("input-csv"):
            if not path.isfile(path.realpath(options.get("input-csv"))):
                raise FileNotFoundError(
                    "{} is not a valid path".format(options.get("input-csv"))
                )
            self.import_georezo_backup(options.get("input-csv"))
        else:
            pass

    # Import methods -----------------------------------------------------
    def import_georezo_backup(self, input_csv_path):
        """
            TO DOC
        :param path input_csv_path:
        """
        # normalize and tests CSV path
        in_csv = path.normpath(input_csv_path)
        if not path.isfile(in_csv):
            raise IOError("Path to the input CSV is not correct.")
        else:
            pass
        # open it an dread it
        with open(in_csv, newline="\n", encoding="utf-8") as csvfile:
            fieldnames = ["rss_id", "title", "abstract", "pub_date"]
            reader = csv.DictReader(csvfile, dialect="pipe", fieldnames=fieldnames)
            ct_new_offers = 0
            for row in reader:
                if GeorezoRSS.objects.filter(id_rss=row.get("rss_id")).exists():
                    logging.info(
                        "Offer can't be imported from input CSV because already exists in DB. RSS ID: {}".format(
                            row.get("rss_id")
                        )
                    )
                else:
                    in_date = arrow.get(row.get("pub_date"))
                    ct_new_offers += 1
                    # insert
                    offer = GeorezoRSS(
                        id_rss=row.get("rss_id"),
                        title=row.get("title"),
                        content=row.get("abstract"),
                        pub_date=in_date.format(),
                        source=True,
                        to_update=True,
                    )
                    offer.save()
            logging.info("{} new offer inserted.".format(ct_new_offers))
        # end of method
        return ct_new_offers
