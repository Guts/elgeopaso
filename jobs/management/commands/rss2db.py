# -*- coding: UTF-8 -*-


# ##################################
# ########## Libraries #############
# ############################################################################

# Standard library
import logging
from argparse import RawTextHelpFormatter
from datetime import timedelta
from pathlib import Path

# 3rd party modules
import arrow
import feedparser

# Django project
from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandParser
from django.db import IntegrityError
from django.db.models import F

from accounts.models import Subscription
from jobs.models import GeorezoRSS, Offer

# submodules
from .analyseur import Analizer

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
        parser = super(Command, self).create_parser(*args, **kwargs)
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
        # parser.add_argument("--rollback", nargs='?', type=bool,
        #                     default=0,
        #                     help='Restore clean offers which have been deleted from their raw copy.')

    def handle(self, *args, **options):
        # analyze specific offer or whole things
        if options.get("offer_id"):
            analyzer = Analizer(options.get("offer_id"), new=options.get("new"))
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
                "El Géo Paso - Analyse terminée",
                "{} new offers added\n"
                "{} offers updated\n"
                "{} orphans offers fixed\n"
                "{} broken raw offers fixed\n"
                "{} broken clean offers fixed\n".format(
                    ct_added, ct_selected, ct_orphans, ct_broken_raw, ct_broken_clean
                ),
                settings.EMAIL_HOST_USER,
                dest,
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
        last_id_file = Path("./last_id_georezo.txt")
        # Get the id of the last offer parsed
        if last_id_file.exists():
            with last_id_file.open(mode="r") as in_file:
                last_id = int(in_file.readline())
            logging.info("Previous offer ID: {}".format(last_id))
        else:
            logging.warning(
                "File with the latest ID offer is missing: {}. Considering latest ID = 0.".format(
                    last_id_file.resolve()
                )
            )
            last_id = 0
        # list to store offers IDs
        li_id = []

        # reset offers counter
        compteur = 0

        # RSS parser
        logging.info(
            "Connecting to the RSS. Expecting {} entries as specified in settings.".format(
                settings.CRAWL_RSS_SIZE
            )
        )
        feed = feedparser.parse(
            url_file_stream_or_string="https://georezo.net/extern.php?fid=10&show={}".format(
                settings.CRAWL_RSS_SIZE
            ),
            agent=settings.USER_AGENT
            # modified=True,
        )

        # test if feed is well-formed
        # https://pythonhosted.org/feedparser/bozo.html#bozo-detection
        if feed.bozo:
            logging.error(
                "RSS feed is badly formed. Parser error: {}.".format(
                    feed.bozo_exception
                )
            )
            return compteur

        # test if feed contains entries
        if not feed.entries:
            # build feed metadata
            feed_metadata = "HTTP status: {}".format(feed.status)
            # feed title
            feed_metadata += " - Title: {}".format(
                feed.feed.get("title", "WARN - Missing title")
            )
            feed_metadata += " (subtitle: {})".format(
                feed.feed.get("subtitle", "no subtitle")
            )
            # get last updated info from feed
            if hasattr(feed.feed, "updated_parsed"):
                feed_metadata += "Last updated: {}".format(
                    arrow.get(feed.feed.updated_parsed).format()
                )

            # log everything
            logging.error(
                "RSS feed is empty, no entries (items) found. Feed info: {}.".format(
                    feed_metadata
                )
            )
            return compteur

        # looping on feed entries
        for entry in feed.entries:
            # get the ID cleaning 'link' markup
            try:
                job_id = int(entry.id.split("#")[1].lstrip("p"))
            except AttributeError as err:
                logging.error(
                    "Feed index corrupted: {} - ({})".format(
                        feed.entries.index(entry), err
                    )
                )
                continue

            # first offer parsed is the last published, so the biggest ID.
            # Put the ID in the dedicated text file.
            if feed.entries.index(entry) == 0:
                with last_id_file.open(mode="w") as out_file:
                    out_file.write(str(job_id))
            else:
                pass

            # formating publication date
            publication_date = arrow.get(entry.published, "ddd, D MMM YYYY HH:mm:ss Z")

            # if entry's ID is greater than ID stored into the file,
            # that means the offer is more recent and has to be processed
            if job_id > last_id:
                try:
                    offer = GeorezoRSS(
                        id_rss=job_id,
                        title=entry.title,
                        content=entry.summary,
                        pub_date=publication_date.format(),
                        source=True,
                        to_update=False,
                    )
                    offer.save()
                    # incrementing counter
                    compteur += 1
                    # adding offer's ID to the list of new offers to process
                    li_id.append(job_id)
                    logging.debug("New offer added: {}".format(job_id))
                except IntegrityError:
                    # in case of duplicated offer
                    logging.warning("Offer ID already exists: {}".format(job_id))
                    continue
                except Exception as error_msg:
                    logging.error(error_msg)
            else:
                logging.debug(
                    "Offer ID inferior to the last registered: {}".format(job_id)
                )
                continue

        # if new offers => launch next processes
        if compteur > 0:
            logging.info("{} new offers to add.".format(len(li_id)))
            analyzer = Analizer(li_id)
            analyzer.analisis()
        else:
            logging.info("No new offer retrieved...")

        return compteur

    def _update_selected_offers(self, force_create: bool = 0):
        """Perform a new analisis on modified raw offers."""
        selected = GeorezoRSS.objects.filter(to_update=True).values_list(
            "id_rss", flat=True
        )
        if selected.count():
            logging.debug(
                "{} offers selected to be re-analyzed.".format(selected.count())
            )
            analyzer = Analizer(list(selected), new=force_create)
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
            logging.debug(
                "{} offers manually updated since last parse".format(updated.count())
            )
            analyzer = Analizer(list(updated), new=0)
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
                "{} orphans (in GeorezoRSS but not in Offer).".format(orphans.count())
            )
            analyzer = Analizer(list(orphans))
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
            analyzer = Analizer(list(raw_orphans))
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
                "{} clean offers were missing their raw offer.".format(no_raw.count())
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
