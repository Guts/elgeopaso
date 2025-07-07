#! python3  # noqa: E265

"""
Module in charge of analyzing raw offers from GeoRezo: extracting contract type,
place, etc. from title and abstract.
"""


# ###########################################################################
# ######### Libraries #############
# #################################

# Standard library
import logging
import re

# Django
from django.db import IntegrityError

# project modules
from elgeopaso.jobs.models import Contract, GeorezoRSS, Offer, Place, Source
from elgeopaso.utils import TextToolbelt

from .parsers import ContentParser, TitleParser

# ##############################################################################
# ########## Globals ###############
# ##################################

# logs
logger = logging.getLogger(__name__)

# timestamps format helpers
_regex_markups = re.compile(r"<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});")

# shortcuts
txt_toolbelt = TextToolbelt()

# ############################################################################
# ########## Classes ##############
# #################################


class GeorezoOfferAnalizer:
    """
    Analyze last offers published on GeoRezo and stored in the main table.
    """

    def __init__(
        self,
        li_offers_ids: list,
        opt_contracts: bool = 1,
        opt_places: bool = 1,
        opt_technos: bool = 1,
        opt_skills: bool = 1,
        opt_words: bool = 1,
        source="GEOREZO_RSS",
        new: bool = 1,
    ):
        """
        :param list li_offers_ids: IDs list of offers to process
        :param bool opt_contracts: parse or not contracts types
        :param bool opt_places: parse or not contracts places
        :param bool opt_technos: parse or not contracts technologies
        :param bool opt_skills: parse or not contracts jobs label
        :param bool opt_words: parse or not contracts words
        :param str source: set offers source
        :param bool new: create or update offer
        """
        # parameters
        self.offers_ids = li_offers_ids
        self.opt_contracts = opt_contracts
        self.opt_places = opt_places
        self.opt_technos = opt_technos
        self.opt_skills = opt_skills
        self.opt_words = opt_words
        self.source = source
        self.new = new
        logger.debug(f"Launching analisis on {len(self.offers_ids)} offers.")
        super().__init__()

    # MAIN METHOD ------------------------------------------------------------

    def analisis(self):
        """Perform analisis on offers."""
        # parse offers
        for offer_id in self.offers_ids:
            self.offer_id = offer_id
            # chekcs if offer has already been added
            if Offer.objects.filter(id_rss=offer_id).exists() and self.new:
                logger.error(f"Offer RSS_ID already exists in DB: {offer_id}")
                continue
            else:
                logger.debug(f"launch analisis on : {self.offer_id}")
                pass
            # get raw offer from georezo_rss table
            raw_offer = GeorezoRSS.objects.get(id_rss=offer_id)

            # -- Title analisis ----------------------
            clean_title = txt_toolbelt.remove_html_markups(raw_offer.title)
            title_parser = TitleParser(offer_id=offer_id, input_title=clean_title)

            # determine contract type
            contract_type = title_parser.parse_contract_type()
            jobs_labels = title_parser.parse_jobs_positions()
            place = title_parser.parse_place(mode=0)

            # -- Content analisis ----------------------
            clean_content = txt_toolbelt.remove_html_markups(raw_offer.content)

            content_parser = ContentParser(
                offer_id=offer_id, input_content=clean_content
            )
            technos = content_parser.parse_technology()

            # add or update offer
            if self.new:
                # add new offer
                clean_offer = Offer(
                    id_rss=offer_id,
                    raw_offer=raw_offer,
                    title=clean_title,
                    content=clean_content,
                    pub_date=raw_offer.pub_date,
                    contract=Contract.objects.get(abbrv=contract_type),
                    source=Source.objects.get(name=self.source),
                    place=Place.objects.get(name=place),
                )
                try:
                    clean_offer.save()
                except IntegrityError as err_msg:
                    logger.error(
                        "Offer RSS_ID ({}) already exists in DB: {}".format(
                            offer_id, err_msg
                        )
                    )
                    continue
            else:
                clean_offer = Offer.objects.select_related().filter(id_rss=offer_id)
                if not clean_offer.exists():
                    logger.info(
                        "Offer to update no longer exists and won't be created: {}".format(
                            offer_id
                        )
                    )
                    continue
                else:
                    pass
                clean_offer.update(
                    title=clean_title,
                    content=clean_content,
                    pub_date=raw_offer.pub_date,
                    contract=Contract.objects.get(abbrv=contract_type),
                    source=Source.objects.get(name=self.source),
                    place=Place.objects.get(name=place),
                )
                clean_offer = Offer.objects.select_related().get(id_rss=offer_id)

            # associate ManyToMany relationships
            clean_offer.technologies.set(technos)
            clean_offer.jobs_positions.set(jobs_labels)
            logger.debug(f"Offer analyzed and inserted jobs.offer: {offer_id}")


# ############################################################################
# #### Stand alone program ########
# #################################
if __name__ == "__main__":
    """standalone execution."""
    pass
