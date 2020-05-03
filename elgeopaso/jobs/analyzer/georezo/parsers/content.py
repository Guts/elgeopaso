#! python3  # noqa: E265

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

from .custom_stopwords import TUP_CUSTOM_STOPWORDS

# ##############################################################################
# ########## Globals ###############
# ##################################

# logs
logger = logging.getLogger(__name__)

# timestamps format helpers
_regex_markups = re.compile(r"<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});")


# ############################################################################
# ########## Classes ##############
# #################################


class ContentParser:
    """Parse content of offers published on GeoRezo to extract informations.

    :param int offer_id: offer ID (for tracing purposes)
    :param str input_content: content to parse
    """

    def __init__(self, offer_id: int, input_content: str):
        """Instanciate content parser module."""
        # parameters
        self.offer_id = offer_id
        self.input_content = input_content

        # tokenize content
        self.tokenized_content = self.parse_words()

    # PARSERS ----------------------------------------------------------------
    def parse_words(self):
        """
        Extraction of words mentioned into the offers. The goal is to perform
        a semantic analysis.
        It's based on NLTK: https://www.nltk.org/
        """
        # get list of common French words to filter
        stop_fr = set(stopwords.words("french"))  # add specific French

        # custom list
        contenu = BeautifulSoup(self.input_content, "html.parser")
        contenu = contenu.get_text("\n")
        contenu = self.remove_html_markups(self.input_content)
        # contenu = self.clean_xml(contenu)
        contenu_tokenized = nltk.word_tokenize(contenu)

        # stop words filter
        for mot in contenu_tokenized:
            if mot in stop_fr or mot in TUP_CUSTOM_STOPWORDS:
                contenu_tokenized = list(filter((mot).__ne__, contenu_tokenized))

        logging.debug("Words parsed: {}".format(len(contenu_tokenized)))

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
