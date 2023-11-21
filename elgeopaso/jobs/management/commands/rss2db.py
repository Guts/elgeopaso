#! python3  # noqa: E265

"""
    Custom Django management command to parse GeoRezo feed and launch analisis.
    See: https://docs.djangoproject.com/fr/2.2/howto/custom-management-commands/
"""

# ############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging
from argparse import RawTextHelpFormatter
from datetime import datetime, timedelta

# 3rd party modules
import arrow

# Django project
from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandParser
from django.db import IntegrityError
from django.db.models import F

from elgeopaso.accounts.models import Subscription

# submodules
from elgeopaso.jobs.analyzer import GeorezoOfferAnalizer
from elgeopaso.jobs.crawlers import GeorezoRssParser
from elgeopaso.jobs.models import GeorezoRSS, Offer

# ############################################################################
# ########### Classes #############
# #################################


class Command(BaseCommand):
    """Commands to manage offers sync and analisis.

    Two main steps:

        1. Crawl GeoRezo RSS to get new offers, analyze it and store into the database.
        2. Relaunch offer analisis on offers which have been manually modified (through the admin)

    :param [type] BaseCommand: [description]

    :raises ValueError: [description]

    :return: [description]
    :rtype: [type]
    """

    args = "<foo bar ...>"
    help = """
        Commands to manage offers sync and analisis. 2 main steps:
        1. Crawl GeoRezo RSS to get new offers, analyze it and store into
        the database.

        2. Relaunch offer analisis on offers which have been manually
        modified (through the admin)
            """.strip()

    # attributes
    now = arrow.now(settings.TIME_ZONE)

    # Parsing options ------------------------------------------------------
    def create_parser(self, *args, **kwargs) -> CommandParser:
        """Super a command parser.

        :return: [description]
        :rtype: CommandParser
        """
        parser = super().create_parser(*args, **kwargs)
        parser.formatter_class = RawTextHelpFormatter
        return parser

    def add_arguments(self, parser: CommandParser):
        """Add arguments to the CLI.

        :param CommandParser parser: command parser
        """
        parser.add_argument(
            "--offer_id",
            nargs="+",
            type=int,
            default=None,
            help="Analyze only a specific offer.",
        )
        parser.add_argument(
            "--new", nargs="?", type=bool, default=0, help="Consider offer(s) as new."
        )
        # parser.add_argument(
        #     "--rollback",
        #     nargs="?",
        #     type=bool,
        #     default=0,
        #     help="Restore clean offers which have been deleted from their raw copy.",
        # )

    def handle(self, *args, **options):
        # analyze specific offer or whole things
        if options.get("offer_id"):
            analyzer = GeorezoOfferAnalizer(
                options.get("offer_id"), new=options.get("new")
            )
            analyzer.analisis()
            return

        # check settings
        if settings.CRAWL_FREQUENCY == "daily":
            self.dt_prev = self.now.shift(days=-1).datetime
        elif settings.CRAWL_FREQUENCY == "hourly":
            self.dt_prev = self.now.shift(hours=-1).datetime
        else:
            logging.error("CRAWL_FREQUENCY has a bad value.")
            raise ValueError("CRAWL_FREQUENCY must be 'hourly' or 'daily'.")

        # launch analisis
        ct_added = self._add_new_offers()
        ct_selected = self._update_selected_offers(force_create=options.get("new"))
        # ct_updated = self._update_modified_offers()
        ct_orphans = self._fix_orphan_offers()
        ct_broken_raw = self._fix_raw_offers_without_clean()
        ct_broken_clean = self._fix_clean_offers_without_raw()

        # LOG and mail notification
        logging.debug(
            "{} new offers added\n"
            "{} offers updated\n"
            "{} orphans offers fixed\n"
            "{} broken raw offers fixed\n"
            "{} broken clean offers fixed\n".format(
                ct_added, ct_selected, ct_orphans, ct_broken_raw, ct_broken_clean
            )
        )
        # recipients
        dest = list(settings.REPORT_RECIPIENTS)
        dest.extend(
            Subscription.objects.select_related()
            .filter(report_hour=True)
            .values_list("user__email", flat=True)
        )

        if not settings.DEBUG:
            send_mail(
                subject="El Géo Paso - Analyse terminée",
                message="{} new offers added\n"
                "{} offers updated\n"
                "{} orphans offers fixed\n"
                "{} broken raw offers fixed\n"
                "{} broken clean offers fixed\n".format(
                    ct_added, ct_selected, ct_orphans, ct_broken_raw, ct_broken_clean
                ),
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=dest,
                fail_silently=False,
            )
        else:
            # send_mail(
            #           "El Géo Paso - Analyse terminée",
            #           "{} new offers added\n"
            #           "{} offers updated\n"
            #           "{} orphans offers fixed"
            #           .format(ct_added,
            #                   ct_selected,
            #                   ct_orphans),
            #           settings.EMAIL_HOST_USER,
            #           dest,
            #           fail_silently=False,
            #           )
            pass
        return

    # New and updated offers -------------------------------------------
    def _add_new_offers(self):
        """Retrieve new offers from RSS feed."""
        #  Using new module
        georezo_rss_parser = GeorezoRssParser(
            items_to_parse=settings.CRAWL_RSS_SIZE, user_agent=settings.USER_AGENT
        )

        li_new_offers_retrieved_from_feed = georezo_rss_parser.parse_new_offers()
        li_new_offers_added = []

        # looping on feed entries
        for entry in li_new_offers_retrieved_from_feed:
            # get the ID cleaning 'link' markup
            job_offer_id = georezo_rss_parser.extract_offer_id_from_url(entry.id)

            # formating publication date
            publication_date_formatted = datetime.strptime(
                entry.published, georezo_rss_parser.FEED_DATETIME_RAW_FORMAT
            )
            # publication_date_formatted = arrow.get(, "ddd, D MMM YYYY HH:mm:ss Z")

            try:
                offer = GeorezoRSS(
                    id_rss=job_offer_id,
                    title=entry.title,
                    content=entry.summary,
                    pub_date=publication_date_formatted,
                    source=True,
                    to_update=False,
                )
                offer.save()
                # adding offer's ID to the list of new offers to process
                li_new_offers_added.append(job_offer_id)
                logging.debug(f"New offer added: {job_offer_id}")
            except IntegrityError:
                # in case of duplicated offer
                logging.warning(f"Offer ID already exists: {job_offer_id}")
                continue
            except Exception as error_msg:
                logging.error(error_msg)

        return len(li_new_offers_added)

    def _update_selected_offers(self, force_create: bool = 0):
        """Perform a new analisis on modified raw offers."""
        selected = GeorezoRSS.objects.filter(to_update=True).values_list(
            "id_rss", flat=True
        )
        if selected.count():
            logging.debug(f"{selected.count()} offers selected to be re-analyzed.")
            analyzer = GeorezoOfferAnalizer(list(selected), new=force_create)
            analyzer.analisis()
            # remove to_update status
            return selected.update(to_update=False)
        else:
            logging.debug("No offer selected to be updated.")
        return selected.count()

    def _update_modified_offers(self):
        """Perform a new analisis on modified raw offers."""
        updated = (
            GeorezoRSS.objects.filter(updated__gte=self.dt_prev)
            .filter(updated__gte=F("created") + timedelta(seconds=60))
            .values_list("id_rss", flat=True)
        )
        if updated.count():
            logging.debug(f"{updated.count()} offers manually updated since last parse")
            analyzer = GeorezoOfferAnalizer(list(updated), new=0)
            analyzer.analisis()
        else:
            logging.debug("No offer updated.")
        return updated.count()

    def _fix_orphan_offers(self):
        """Sometimes offers parsing fails. This methods check 'orphans'"""
        grss_ids = GeorezoRSS.objects.values_list("id_rss", flat=True)
        orphans = Offer.objects.exclude(id_rss__in=grss_ids).values_list(
            "id_rss", flat=True
        )
        if orphans.count():
            logging.debug(
                f"{orphans.count()} orphans (in GeorezoRSS but not in Offer)."
            )
            analyzer = GeorezoOfferAnalizer(list(orphans))
            analyzer.analisis()
        else:
            logging.debug("No orphan offer found.")
        # end of method
        return orphans.count()

    def _fix_raw_offers_without_clean(self):
        """Raw offers which do not have a related clean offer."""
        offers_clean_ids = Offer.objects.values_list("id_rss", flat=True)
        raw_orphans = GeorezoRSS.objects.exclude(
            id_rss__in=offers_clean_ids
        ).values_list("id_rss", flat=True)
        if raw_orphans.count():
            logging.debug(
                "{} raw_orphans (in GeorezoRSS but not in Offer).".format(
                    raw_orphans.count()
                )
            )
            analyzer = GeorezoOfferAnalizer(list(raw_orphans))
            analyzer.analisis()
        else:
            logging.debug("No raw_orphan offer found.")
        # end of method
        return raw_orphans.count()

    def _fix_clean_offers_without_raw(self):
        """Offers which do not have a related raw offer."""
        no_raw = Offer.objects.select_related().filter(raw_offer__isnull=True)
        if no_raw.count():
            for i in no_raw:
                o = Offer.objects.select_related().filter(id_rss=i.id_rss)
                raw_offer = GeorezoRSS.objects.get(id_rss=i.id_rss)
                o.update(raw_offer=raw_offer)
            logging.debug(
                f"{no_raw.count()} clean offers were missing their raw offer."
            )
        else:
            logging.debug("All clean offers have a related raw offer.")
        # end of method
        return no_raw.count()


# ############################################################################
# #### Stand alone program ########
# #################################
if __name__ == "__main__":
    """standalone execution."""
    # logging with debug
    logging.basicConfig(level=logging.DEBUG)
