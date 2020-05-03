#! python3  # noqa: E265
# -*- coding: utf-8 -*-

"""
    Content parser.
"""


# ###########################################################################
# ######### Libraries #############
# #################################

# Standard library
import html
import logging
import re

# 3rd party modules
import nltk
from bs4 import BeautifulSoup
from nltk.corpus import stopwords

# project modules
from elgeopaso.jobs.models import (
    JobPosition,
    JobPositionVariations,
    Source,
    Technology,
    TechnologyVariations,
)

# ##############################################################################
# ########## Globals ###############
# ##################################

# timestamps format helpers
_regex_markups = re.compile(r"<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});")


# ############################################################################
# ########## Classes ##############
# #################################


class ContentParser:
    """Parse content of offers published on GeoRezo to extract informations.

    :param str input_content: content to parse
    :param bool new: create or update offer. Defaults to: 1 - optional
    """

    def __init__(self, input_content: str, new: bool = 1):
        """Instanciate content parser module."""
        # parameters
        self.input_content = input_content
        self.new = new

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
