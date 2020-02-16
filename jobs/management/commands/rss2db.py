# -*- coding: UTF-8 -*-

# ############################################################################
# ########## Libraries #############
# ##################################
# Standard library
from argparse import RawTextHelpFormatter
from datetime import timedelta
import logging
from os import path

# 3rd party modules
import arrow
import feedparser

# Django project
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
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
    args = '<foo bar ...>'
    help = """
        Commands to manage offers sync and analisis. 2 main steps:
        1. Crawl GeoRezo RSS to get new offers, analyze it and store into
        the database.

        2. Relaunch offer analisis on offers which have been manually
        modified (through the admin)
            """.strip()

    # attributes
    now = arrow.now(settings.TIME_ZONE)
    logger = logging.getLogger("ElPaso")

    # Parsing options ------------------------------------------------------
    def create_parser(self, *args, **kwargs):
        parser = super(Command, self).create_parser(*args, **kwargs)
        parser.formatter_class = RawTextHelpFormatter
        return parser

    def add_arguments(self, parser):
        parser.add_argument("--offer_id", nargs='+', type=int,
                            default=None,
                            help='Analyze only a specific offer.')
        parser.add_argument("--new", nargs='?', type=bool,
                            default=0,
                            help='Consider offer(s) as new.')
        # parser.add_argument("--rollback", nargs='?', type=bool,
        #                     default=0,
        #                     help='Restore clean offers which have been deleted from their raw copy.')

    def handle(self, *args, **options):
        # analyze specific offer or whole things
        if options.get("offer_id"):
            analyzer = Analizer(options.get("offer_id"),
                                new=options.get("new"))
            analyzer.analisis()
            return

        # check settings
        if settings.CRAWL_FREQUENCY == "daily":
            self.dt_prev = self.now.shift(days=-1).datetime
        elif settings.CRAWL_FREQUENCY == "hourly":
            self.dt_prev = self.now.shift(hours=-1).datetime
        else:
            self.logger.error("CRAWL_FREQUENCY has a bad value.")
            raise ValueError("CRAWL_FREQUENCY must be 'hourly' or 'daily'.")

        # launch analisis
        ct_added = self._add_new_offers()
        ct_selected = self._update_selected_offers(force_create=options.get("new"))
        # ct_updated = self._update_modified_offers()
        ct_orphans = self._fix_orphan_offers()
        ct_broken_raw = self._fix_raw_offers_without_clean()
        ct_broken_clean = self._fix_clean_offers_without_raw()

        # LOG and mail notification
        self.logger.debug("{} new offers added\n"
                          "{} offers updated\n"
                          "{} orphans offers fixed\n"
                          "{} broken raw offers fixed\n"
                          "{} broken clean offers fixed\n"
                          .format(ct_added,
                                  ct_selected,
                                  ct_orphans,
                                  ct_broken_raw,
                                  ct_broken_clean))
        # recipients
        dest = settings.RECIPIENTS
        dest.extend(Subscription.objects
                    .select_related()
                    .filter(report_hour=True)
                    .values_list("user__email",
                                 flat=True))

        if not settings.DEBUG:
            send_mail(
                      "El Géo Paso - Analyse terminée",
                      "{} new offers added\n"
                      "{} offers updated\n"
                      "{} orphans offers fixed\n"
                      "{} broken raw offers fixed\n"
                      "{} broken clean offers fixed\n"
                      .format(ct_added,
                              ct_selected,
                              ct_orphans,
                              ct_broken_raw,
                              ct_broken_clean),
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
        """Adds new offer from RSS feed."""
        # Get the id of the last offer parsed
        with open(path.abspath(r'last_id_georezo.txt'), 'r') as f:
            last_id = int(f.readline())
        self.logger.debug("Previous offer ID: {}".format(last_id))
        # list to store offers IDs
        li_id = []

        # reset offers counter
        compteur = 0

        # RSS parser
        feed = feedparser.parse('https://georezo.net/extern.php?fid=10&show={}'
                                .format(settings.CRAWL_RSS_SIZE))
        self.logger.debug("Parser created")

        # looping on feed entries
        for entry in feed.entries:
            # get the ID cleaning 'link' markup
            try:
                job_id = int(entry.id.split('#')[1].lstrip('p'))
            except AttributeError as e:
                self.logger.error("Feed index corrupted: {} - ({})"
                                  .format(feed.entries.index(entry), e))
                continue

            # first offer parsed is the last published, so the biggest ID.
            # Put the ID in the dedicated text file.
            if feed.entries.index(entry) == 0:
                with open(path.abspath(r'last_id_georezo.txt'), 'w') as f:
                    f.write(str(job_id))
            else:
                pass

            # formating publication date
            publication_date = arrow.get(entry.published,
                                         "ddd, D MMM YYYY HH:mm:ss Z")

            # if entry's ID is greater than ID stored into the file,
            # that means the offer is more recent and has to be processed
            if job_id > last_id:
                try:
                    offer = GeorezoRSS(id_rss=job_id,
                                       title=entry.title,
                                       content=entry.summary,
                                       pub_date=publication_date.format(),
                                       source=True,
                                       to_update=False)
                    offer.save()
                    # incrementing counter
                    compteur += 1
                    # adding offer's ID to the list of new offers to process
                    li_id.append(job_id)
                    self.logger.debug("New offer added: {}".format(job_id))
                except IntegrityError:
                    # in case of duplicated offer
                    self.logger.error("Offer ID already exists: {}"
                                      .format(job_id))
                    continue
                except Exception as error_msg:
                    self.logger.error(error_msg)
            else:
                self.logger.debug("Offer ID inferior to the last registered: {}"
                                 .format(job_id))
                pass

        # if new offers => launch next processes
        if compteur > 0:
            self.logger.debug("New offers IDs: " + str(li_id))
            analyzer = Analizer(li_id)
            analyzer.analisis()
        else:
            pass

        return compteur

    def _update_selected_offers(self, force_create: bool=0):
        """Perform a new analisis on modified raw offers."""
        selected = GeorezoRSS.objects.filter(to_update=True)\
                                     .values_list("id_rss", flat=True)
        if selected.count():
            self.logger.debug("{} offers selected to be re-analyzed."
                              .format(selected.count()))
            analyzer = Analizer(list(selected),
                                new=force_create)
            analyzer.analisis()
            # remove to_update status
            return selected.update(to_update=False)
        else:
            self.logger.debug("No offer selected to be updated.")
        return selected.count()

    def _update_modified_offers(self):
        """Perform a new analisis on modified raw offers."""
        updated = GeorezoRSS.objects.filter(updated__gte=self.dt_prev)\
                                    .filter(updated__gte=F("created") + timedelta(seconds=60))\
                                    .values_list("id_rss", flat=True)
        if updated.count():
            self.logger.debug("{} offers manually updated since last parse"
                              .format(updated.count()))
            analyzer = Analizer(list(updated), new=0)
            analyzer.analisis()
        else:
            self.logger.debug("No offer updated.")
        return updated.count()

    def _fix_orphan_offers(self):
        """Sometimes offers parsing fails. This methods check 'orphans'"""
        grss_ids = GeorezoRSS.objects.values_list("id_rss", flat=True)
        orphans = Offer.objects.exclude(id_rss__in=grss_ids)\
                               .values_list("id_rss", flat=True)
        if orphans.count():
            self.logger.debug("{} orphans (in GeorezoRSS but not in Offer)."
                             .format(orphans.count()))
            analyzer = Analizer(list(orphans))
            analyzer.analisis()
        else:
            self.logger.debug("No orphan offer found.")
        # end of method
        return orphans.count()

    def _fix_raw_offers_without_clean(self):
        """Raw offers which do not have a related clean offer."""
        offers_clean_ids = Offer.objects.values_list("id_rss", flat=True)
        raw_orphans = GeorezoRSS.objects.exclude(id_rss__in=offers_clean_ids)\
                                .values_list("id_rss", flat=True)
        if raw_orphans.count():
            self.logger.debug("{} raw_orphans (in GeorezoRSS but not in Offer)."
                              .format(raw_orphans.count()))
            analyzer = Analizer(list(raw_orphans))
            analyzer.analisis()
        else:
            self.logger.debug("No raw_orphan offer found.")
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
            self.logger.debug("{} clean offers were missing their raw offer."
                              .format(no_raw.count()))
        else:
            self.logger.debug("All clean offers have a related raw offer.")
        # end of method
        return no_raw.count()

# ############################################################################
# #### Stand alone program ########
# #################################
if __name__ == '__main__':
    """standalone execution."""
