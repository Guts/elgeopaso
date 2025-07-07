#! python3  # noqa: E265


"""
Title parser.
"""


# ###########################################################################
# ######### Libraries #############
# #################################

# Standard library
import logging
import re

# project modules
from elgeopaso.jobs.models import (
    Contract,
    ContractVariations,
    JobPosition,
    JobPositionVariations,
    Place,
    PlaceVariations,
)
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


class TitleParser:
    """Parse title of offers published on GeoRezo to extract informations.

    :param int offer_id: offer ID (for tracing purposes)
    :param str input_title: title to parse
    """

    def __init__(self, offer_id: int, input_title: str):
        """Instanciate title parser module."""
        # parameters
        self.offer_id = offer_id
        self.input_title = input_title

        # tokenize content
        self.tokenized_title = txt_toolbelt.tokenize(self.input_title)

    # PARSERS ----------------------------------------------------------------
    def parse_contract_type(self) -> Contract:
        """Extraction of types of contracts: CDI, CDD, mission, volontariat, etc.

        In theory, offer's title is formatted to contain the type between []...
        """
        # clean the title: excluding text out of brackets
        try:
            contract = self.input_title.split("[")[1].split("]")[0]
        except IndexError:
            logging.warning(f"Title bad formatted. Offer RSS ID: {self.offer_id}")
            contract = self.input_title.split("]")[0].lstrip("[")

        logging.debug(f"Contract extracted from title: {contract}")
        contract = contract.lower()

        # find a contract match
        if Contract.objects.filter(abbrv=contract).exists():
            return Contract.objects.get(label=contract)
        elif ContractVariations.objects.filter(label=contract).exists():
            contract_var = ContractVariations.objects.get(label=contract).name
            return Contract.objects.get(abbrv=contract_var)
        else:
            return Contract.objects.get(abbrv="ND")

    def parse_jobs_positions(self) -> list:
        """Identify job position ('métier') from passed string."""
        jobs_positions_matched = []

        # parse tokenized
        for word in self.tokenized_title:
            if JobPositionVariations.objects.filter(label=word.lower()).exists():
                job_label = JobPositionVariations.objects.get(label=word.lower()).name
                jobs_positions_matched.append(JobPosition.objects.get(name=job_label))
            else:
                continue

        logger.debug(f"Jobs positions identified: {jobs_positions_matched}")
        return jobs_positions_matched

    def parse_place(self, mode: int = 0) -> Place:
        """
        Extraction of types of contracts: CDI, CDD, mission, volontariat, etc.
        In theory, place information is wihtin parenthesis '()'.

        :param int mode: 0 = STRICT regex (default): only digits between ()
                         1 = MEDIUM regex: alphanumeric between ()
                         2 = SOFT regex: alphanumeric code outside ()
        """
        # removing contract type between []
        try:
            title = self.input_title.split("[")[1].split("]")[1]
            logging.debug(f"Title without contract: {title}")
        except IndexError:
            logging.error(f"Title bad formatted. Offer RSS ID: {self.offer_id}")
            title = self.input_title

        # extract with regex
        if not mode:
            dpt_code = re.findall(r"\((\d+)\)", title)
            logging.debug(f"STRICT regex applied: {dpt_code}")
        elif mode == 1:
            dpt_code = re.findall(r"\((2[AB]|[0-9]+)\)", title)
            logging.debug(f"MEDIUM regex applied: {dpt_code}")
        elif mode == 2:
            dpt_code = re.findall(r"(2[AB]|[0-9]+)", title)
            logging.debug(f"SOFT regex applied: {dpt_code}")
        else:
            raise TypeError("'mode' parameter only accepts an integer [0-2]")

        # match French department code
        if len(dpt_code) == 1:
            if Place.objects.filter(code=dpt_code[0]).exists():
                place_name = Place.objects.get(code=dpt_code[0]).name
                logging.debug(f"Place code MATCHED in title: {dpt_code}")
                return Place.objects.get(name=place_name)
            else:
                logging.debug(f"Place code MATCHED in title: {title}")
                # try again
                if mode < 2:
                    return self.parse_place(mode=mode + 1)
                else:
                    pass
        elif len(dpt_code) > 1:
            logging.warning(
                "More than possible department code found: {}.".format(
                    ";".join(dpt_code)
                )
            )
            # try again
            if mode < 2:
                return self.parse_place(mode=mode + 1)
            else:
                pass
        elif not len(dpt_code):
            logging.warning(
                "No place code found in title." " Trying to find a place anyway..."
            )
            t_place = title[title.find("(") + 1 : title.find(")")]
            if "," in t_place:
                t_place = t_place.lower().split(",")
            else:
                t_place = t_place.lower().split()
                pass
            # try to get a match in place variations
            for i in t_place:
                if PlaceVariations.objects.filter(label=i).exists():
                    pv = PlaceVariations.objects.get(label=i).name
                    logging.debug(f"Place found: {i}")
                    return Place.objects.get(name=pv)
                else:
                    logging.debug(f"No place found in: {i}")
            # try again
            if mode < 2:
                return self.parse_place(mode=mode + 1)
            else:
                logging.warning(f"No place found in title: {self.input_title}")
                pass

        # method ending if no place found during various attempts
        return "ND"


# ############################################################################
# #### Stand alone program ########
# #################################
if __name__ == "__main__":
    """standalone execution."""
    pass
