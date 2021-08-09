#! python3  # noqa: E265

# #############################################################################
# ######### Libraries #############
# #################################
# Standard library
from argparse import RawTextHelpFormatter

# Django project
from django.core.management.base import BaseCommand

# submodules
from elgeopaso.jobs.analyzer import GeorezoOfferAnalizer
from elgeopaso.jobs.models import GeorezoRSS, Offer

# #############################################################################
# ########### Classes #############
# #################################


class Command(BaseCommand):
    args = "<foo bar ...>"
    help = (
        "Empty tables and launch GeorezoOfferAnalizer from the whole georezo_rss table."
    )

    # Parsing options ------------------------------------------------------

    def create_parser(self, *args, **kwargs):
        parser = super(Command, self).create_parser(*args, **kwargs)
        parser.formatter_class = RawTextHelpFormatter
        return parser

    def add_arguments(self, parser):
        parser.add_argument(
            "--quantity",
            nargs="+",
            type=int,
            default=[
                100,
            ],
            help="Quantity of offers to compute." " To compute the whole DB, use '-1'",
        )

    def handle(self, *args, **options):
        """List commands to launch."""
        self._reset_analisis(
            quantity=int(
                options.get(
                    "quantity",
                    [
                        100,
                    ],
                )[0]
            )
        )

    # New and updated offers -------------------------------------------
    def _reset_analisis(self, quantity: int = 100):
        """Perform a whole analisis from the raw offers table."""
        # flush everything in Offer table: BE CAREFUL
        Offer.objects.all().delete()
        raw_offers_rss = GeorezoRSS.objects.values_list("id_rss").order_by("id_rss")
        li_raw_offers_rss = [raw_offer[0] for raw_offer in raw_offers_rss]

        # reset whole DB or just the specified quantity
        if quantity == -1:
            analyzer = GeorezoOfferAnalizer(li_raw_offers_rss)
            analyzer.analisis()
        else:
            analyzer = GeorezoOfferAnalizer(li_raw_offers_rss[:quantity])
            analyzer.analisis()
