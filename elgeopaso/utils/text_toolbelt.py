#! python3  # noqa: E265


"""
Tool.
"""


# ###########################################################################
# ######### Libraries #############
# #################################

# Standard library
import html
import logging
import re

# 3rd party
import nltk
from bs4 import BeautifulSoup
from nltk.corpus import stopwords

# submodules
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


class TextToolbelt:
    """Tools to manipulate text: tokenize, clean, etc."""

    def __init__(self):
        """Instanciate module."""
        super().__init__()

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

    @classmethod
    def tokenize(cls, input_content: str) -> list:
        """Extraction of words mentioned into the offers. The goal is to perform
        a semantic analysis. Mainly based on NLTK: https://www.nltk.org/.

        :param str input_content: input text to parse and tokenize

        :return: list of toknized words
        :rtype: list
        """
        # get list of common French words to filter
        stop_fr = set(stopwords.words("french"))  # add specific French

        # custom list
        contenu = BeautifulSoup(input_content, "html.parser")
        contenu = contenu.get_text("\n")
        contenu = cls.remove_html_markups(input_content)
        # contenu = self.clean_xml(contenu)
        contenu_tokenized = nltk.word_tokenize(contenu)

        # stop words filter
        for mot in contenu_tokenized:
            if mot in stop_fr or mot in TUP_CUSTOM_STOPWORDS:
                contenu_tokenized = list(filter((mot).__ne__, contenu_tokenized))

        logger.debug(f"Words parsed: {len(contenu_tokenized)}")

        return contenu_tokenized


# ############################################################################
# #### Stand alone program ########
# #################################
if __name__ == "__main__":
    """standalone execution."""
    pass
