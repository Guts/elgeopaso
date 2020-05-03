# -*- coding: utf-8 -*-
#! python3  # noqa: E265

"""
    Module in charge of analyzing raw offers from GeoRezo: extracting contract type,
    place, etc. from title and abstract.
"""


# ###########################################################################
# ######### Libraries #############
# #################################

# Standard library
import html
import logging
import re

# Django
from django.db import IntegrityError

# 3rd party modules
import nltk
from bs4 import BeautifulSoup
from nltk.corpus import stopwords

# project modules
from elgeopaso.jobs.models import (
    Contract,
    GeorezoRSS,
    JobPosition,
    JobPositionVariations,
    Offer,
    Place,
    Source,
    Technology,
    TechnologyVariations,
)

from .parsers import ContentParser, TitleParser

# ##############################################################################
# ########## Globals ###############
# ##################################

# timestamps format helpers
_regex_markups = re.compile(r"<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});")


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
        logging.debug("Launching analisis on {} offers.".format(len(self.offers_ids)))
        super(GeorezoOfferAnalizer, self).__init__()

    # MAIN METHOD ------------------------------------------------------------

    def analisis(self):
        """Perform analisis on offers."""
        # parse offers
        for offer_id in self.offers_ids:
            self.offer_id = offer_id
            # chekcs if offer has already been added
            if Offer.objects.filter(id_rss=offer_id).exists() and self.new:
                logging.error("Offer RSS_ID already exists in DB: {}".format(offer_id))
                continue
            else:
                logging.debug("launch analisis on : {}".format(self.offer_id))
                pass
            # get raw offer from georezo_rss table
            raw_offer = GeorezoRSS.objects.get(id_rss=offer_id)

            # -- Title analisis ----------------------
            clean_title = self.remove_html_markups(raw_offer.title)
            title_parser = TitleParser(offer_id=offer_id, input_title=clean_title)

            # determine contract type
            contract_type = title_parser.parse_contract_type()
            place = title_parser.parse_place(mode=0)

            # -- Content analisis ----------------------
            # clean content
            clean_content = self.remove_html_markups(raw_offer.content)
            # content cleaning and nltk tokenizing
            content_words = self.parse_words(raw_offer.content)
            # print(content_words)
            content_title = self.parse_words(raw_offer.title)
            technos = self.parse_technology(content_words)
            jobs_labels = self.parse_jobs_positions(content_title)

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
                    logging.error(
                        "Offer RSS_ID ({}) already exists in DB: {}".format(
                            offer_id, err_msg
                        )
                    )
                    continue
            else:
                clean_offer = Offer.objects.select_related().filter(id_rss=offer_id)
                if not clean_offer.exists():
                    logging.info(
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
            logging.debug("Offer analyzed and inserted jobs.offer: {}".format(offer_id))

    # PARSERS ----------------------------------------------------------------
    def parse_words(self, offer_raw_content):
        """
        Extraction of words mentioned into the offers. The goal is to perform
        a semantic analysis.
        It's based on NLTK: https://www.nltk.org/
        """
        # get list of common French words to filter
        stop_fr = set(stopwords.words("french"))  # add specific French

        # custom list
        li_stop_custom = (
            "(",
            ")",
            "...",
            ".",
            ":",
            ";",
            "/",
            "nbsp",
            "&",
            "#",
            ",",
            "-",
            ":",
            "http",
            "img",
            "br",
            "amp",
            "<",
            ">",
            "%",
            "border",
            "*",
            "border=",
            "les",
            "leurs",
            "&",
            "#",
            "-",
            "+",
            ":",
            ".",
            ";",
            "à",
            "où",
            "des",
            ",",
            "nbsp",
            "De",
            "Des",
            "et",
            "en",
            "(",
            ")",
            "pour",
            "plus",
            "sein",
            "sous",
            "Les",
            "auprès",
            "etc",
            "the",
            "for",
            "ème",
            "via",
            "Vos",
            "dès",
            "plein",
            "tel",
            "etc.",
            "etc..",
            "Ces",
            "tél",
            "cela",
            "ceci",
            "cet",
        )

        contenu = BeautifulSoup(offer_raw_content, "html.parser")
        contenu = contenu.get_text("\n")
        contenu = self.remove_html_markups(offer_raw_content)
        # contenu = self.clean_xml(contenu)
        contenu_tokenized = nltk.word_tokenize(contenu)
        # print(len(contenu_tokenized))

        # stop words filter
        for mot in contenu_tokenized:
            if mot in stop_fr or mot in li_stop_custom:
                contenu_tokenized = list(filter((mot).__ne__, contenu_tokenized))

        logging.debug("Words parsed: {}".format(len(contenu_tokenized)))

        # print(len(contenu_tokenized))
        return contenu_tokenized

    def parse_technology(self, offer_content_tokenized):
        """TO DOCUMENT
        """
        technos_matched = []
        # print(sorted(offer_content_tokenized))
        for word in offer_content_tokenized:
            if TechnologyVariations.objects.filter(label=word.lower()).exists():
                techno_name = TechnologyVariations.objects.get(label=word.lower()).name
                technos_matched.append(Technology.objects.get(name=techno_name))
            else:
                continue
        logging.debug("Technologies identified: {}".format(technos_matched))
        return technos_matched

    def parse_jobs_positions(self, offer_content_tokenized):
        """TO DOCUMENT
        """
        jobs_positions_matched = []
        for word in offer_content_tokenized:
            if JobPositionVariations.objects.filter(label=word.lower()).exists():
                job_label = JobPositionVariations.objects.get(label=word.lower()).name
                jobs_positions_matched.append(JobPosition.objects.get(name=job_label))
            else:
                continue
        logging.debug("Jobs positions identified: {}".format(jobs_positions_matched))
        return jobs_positions_matched

    # ------------ UTILITIES -------------------------------------------------
    @classmethod
    def remove_html_markups(cls, html_text: str, cleaner: str = "bs-lxml") -> str:
        """Very basic cleaner for HTML markups.

        :param str html_text: text to be clean
        :param str cleaner: Which lib to use to clean the text:
          - "bs-lxml": Beautifulsoup4 + LXML - Default.
          - "psl-only": Python Standard Library only (html + regex)

        :return: clean text
        :rtype: str
        """
        # with BeautifulSoup + LXML
        if cleaner == "bs-lxml":
            cleaned_text = BeautifulSoup(html_text, "lxml").text
        elif cleaner == "psl-only":
            # convert HTML5 characters into str.
            # See: https://docs.python.org/3/library/html.html#html.unescape
            html_text = html.unescape(html_text)
            cleaned_text = _regex_markups.sub(" ", html_text)

        return cleaned_text


# ############################################################################
# #### Stand alone program ########
# #################################
if __name__ == "__main__":
    """standalone execution."""
    pass
