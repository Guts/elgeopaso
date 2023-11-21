#! python3  # noqa: E265

"""
    Content parser.
"""


# ###########################################################################
# ######### Libraries #############
# #################################

# Standard library
import logging
import re

# project modules
from elgeopaso.jobs.models import Technology, TechnologyVariations
from elgeopaso.utils import TextToolbelt

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
        self.tokenized_content = txt_toolbelt.tokenize(self.input_content)

    # PARSERS ----------------------------------------------------------------
    def parse_technology(self) -> list:
        """Identify technologies in content."""
        technos_matched = []

        # parse tokenized content
        for word in self.tokenized_content:
            if TechnologyVariations.objects.filter(label=word.lower()).exists():
                techno_name = TechnologyVariations.objects.get(label=word.lower()).name
                technos_matched.append(Technology.objects.get(name=techno_name))
            else:
                continue
        logger.debug(f"Technologies identified: {technos_matched}")
        return technos_matched


# ############################################################################
# #### Stand alone program ########
# #################################
if __name__ == "__main__":
    """standalone execution."""
    pass
