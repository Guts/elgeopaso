# -*- coding: UTF-8 -*-
#! python3  # noqa: E265

"""
    Class to analyze raw offers, extracting contract type,
    place, etc. from title and abstract.
"""


# ###########################################################################
# ######### Libraries #############
# #################################

# Standard library
import html
import logging
import re
import sys
from itertools import zip_longest
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape  # '<' -> '&lt;'

# Django
from django.conf import settings
from django.db import IntegrityError

# 3rd party modules
import arrow
import nltk
from bs4 import BeautifulSoup
from nltk.corpus import stopwords

# project modules
from jobs.models import (
    Contract,
    ContractVariations,
    GeorezoRSS,
    JobPosition,
    JobPositionVariations,
    Offer,
    Place,
    PlaceVariations,
    Source,
    Technology,
    TechnologyVariations,
)

# #############################################################################
# ########## Functions ############
# #################################


# Print iterations progress
def printProgress(
    iteration, total, prefix="", suffix="", decimals=1, barLength=100, fill="█"
):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        barLength   - Optional  : character length of bar (Int)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(barLength * iteration // total)
    bar = fill * filledLength + "-" * (barLength - filledLength)
    sys.stdout.write("\r%s |%s| %s%s %s" % (prefix, bar, percent, "%", suffix)),
    if iteration == total:
        sys.stdout.write("\n")
    sys.stdout.flush()


# ############################################################################
# ########## Classes ##############
# #################################


class Analizer(object):
    """
    Analyze of last offers published on GeoRezo and stored in the main table.
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
        super(Analizer, self).__init__()
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

    # MAIN METHOD ------------------------------------------------------------

    def analisis(self):
        """Perform analisis on offers."""
        # progress bar ony if debug mode is disabled
        if not settings.DEBUG:
            i = 0  # start
            printProgress(
                i,
                total=len(self.offers_ids),
                prefix="Progress:",
                suffix="Complete",
                barLength=50,
            )
        else:
            pass

        # parse offers
        for offer_id in self.offers_ids:
            self.offer_id = offer_id
            # chekcs if offer has already been added
            if Offer.objects.filter(id_rss=offer_id).exists() and self.new:
                logging.error("Offer RSS_ID already exists in DB: {}".format(offer_id))
                # Update Progress Bar only if debug mode is disabled
                if not settings.DEBUG:
                    i += 1
                    printProgress(
                        i,
                        len(self.offers_ids),
                        prefix="Progress:",
                        suffix="Complete",
                        barLength=50,
                    )
                else:
                    pass
                continue
            else:
                logging.debug("launch analisis on : {}".format(self.offer_id))
                pass
            # get raw offer from georezo_rss table
            raw_offer = GeorezoRSS.objects.get(id_rss=offer_id)
            # clean title
            clean_title = self.remove_tags(raw_offer.title)
            # determine contract type
            contract_type = self.parse_contract_type(clean_title)
            place = self.parse_place(clean_title, mode=0)
            # clean content
            clean_content = self.remove_tags(raw_offer.content)
            # content cleaning and nltk tokenizing
            content_words = self.parse_words(raw_offer.content)
            # print(content_words)
            content_title = self.parse_words(raw_offer.title)
            technos = self.parse_technology(content_words)
            jobs_labels = self.parse_jobs_positions(content_title)
            # determine offer week number YYYYWW
            week_number = self.define_week_number(raw_offer.pub_date)

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
                    week=week_number,
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
                    # Update Progress Bar only if debug mode is disabled
                    if not settings.DEBUG:
                        i += 1
                        printProgress(
                            i,
                            len(self.offers_ids),
                            prefix="Progress:",
                            suffix="Complete",
                            barLength=50,
                        )
                    else:
                        pass
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
                    week=week_number,
                    source=Source.objects.get(name=self.source),
                    place=Place.objects.get(name=place),
                )
                clean_offer = Offer.objects.select_related().get(id_rss=offer_id)

            # associate ManyToMany relationships
            clean_offer.technologies.set(technos)
            clean_offer.jobs_positions.set(jobs_labels)
            logging.debug("Offer analyzed and inserted jobs.offer: {}".format(offer_id))
            # Update Progress Bar only if debug mode is disabled
            if not settings.DEBUG:
                i += 1
                printProgress(
                    i,
                    len(self.offers_ids),
                    prefix="Progress:",
                    suffix="Complete",
                    barLength=50,
                )
            else:
                pass

    # PARSERS ----------------------------------------------------------------

    def parse_contract_type(self, offer_clean_title: str):
        """
        Extraction of types of contracts: CDI, CDD, mission, volontariat, etc.
        In theory, offer's title is formatted to contain the type between []

        :param str offer_clean_title: clean title
        """
        # clean the title: excluding text out of brackets
        try:
            contract = offer_clean_title.split("[")[1].split("]")[0]
        except IndexError:
            logging.warning(
                "Title bad formatted. Offer RSS ID: {}".format(self.offer_id)
            )
            contract = offer_clean_title.split("]")[0].lstrip("[")

        logging.debug("Contract extracted from title: {}".format(contract))
        contract = contract.lower()

        # find a contract match
        if Contract.objects.filter(abbrv=contract).exists():
            return Contract.objects.get(label=contract)
        elif ContractVariations.objects.filter(label=contract).exists():
            contract_var = ContractVariations.objects.get(label=contract).name
            return Contract.objects.get(abbrv=contract_var)
        else:
            return Contract.objects.get(abbrv="ND")

    def parse_place(self, offer_raw_title: str, mode: int = 0):
        """
        Extraction of types of contracts: CDI, CDD, mission, volontariat, etc.
        In theory, place information is wihtin parenthesis '()'.

        :param str offer_raw_title: offer title
        :param int mode: 0 = STRICT regex (default): only digits between ()
                         1 = MEDIUM regex: alphanumeric between ()
                         2 = SOFT regex: alphanumeric code outside ()
        """
        # removing contract type between []
        try:
            title = offer_raw_title.split("[")[1].split("]")[1]
            logging.debug("Title without contract: {}".format(title))
        except IndexError:
            logging.error("Title bad formatted. Offer RSS ID: {}".format(self.offer_id))
            title = offer_raw_title

        # extract with regex
        if not mode:
            dpt_code = re.findall("\((\d+)\)", title)
            logging.debug("STRICT regex applied: {}".format(dpt_code))
        elif mode == 1:
            dpt_code = re.findall("\((2[AB]|[0-9]+)\)", title)
            logging.debug("MEDIUM regex applied: {}".format(dpt_code))
        elif mode == 2:
            dpt_code = re.findall("(2[AB]|[0-9]+)", title)
            logging.debug("SOFT regex applied: {}".format(dpt_code))
        else:
            raise TypeError("'mode' parameter only accepts an integer [0-2]")

        # match French department code
        if len(dpt_code) == 1:
            if Place.objects.filter(code=dpt_code[0]).exists():
                place_name = Place.objects.get(code=dpt_code[0]).name
                logging.debug("Place code MATCHED in title: {}".format(dpt_code))
                return Place.objects.get(name=place_name)
            else:
                logging.debug("Place code MATCHED in title: {}".format(title))
                # try again
                if mode < 2:
                    return self.parse_place(title, mode=mode + 1)
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
                return self.parse_place(title, mode=mode + 1)
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
                    logging.debug("Place found: {}".format(i))
                    return Place.objects.get(name=pv)
                else:
                    logging.debug("No place found in: {}".format(i))
            # try again
            if mode < 2:
                return self.parse_place(title, mode=mode + 1)
            else:
                logging.warning("No place found in title: {}".format(offer_raw_title))
                pass

        # method ending if no place found during various attempts
        return "ND"

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
        contenu = self.remove_tags(offer_raw_content)
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

    def define_week_number(self, offer_raw_datetime):
        """
        Extracts year and week number from offer publication datetime
        for more convenience in graphical representation.
        """
        return "{}{}".format(
            arrow.get(offer_raw_datetime).isocalendar()[0],
            str(arrow.get(offer_raw_datetime).isocalendar()[1]).zfill(2),
        )

    # ------------ UTILITIES -------------------------------------------------

    def remove_tags(self, html_text):
        """Very basic cleaner for HTML markups.

        :param [type] html_text: [description]

        :return: [description]
        :rtype: [type]

        :example:

        .. code-block:: python

            # here comes an example in Python
        """
        html_text = html.unescape(html_text)
        try:
            text = " ".join(ET.fromstring(html_text).itertext())
        except Exception as err:
            logging.debug(
                "Error cleaning HTML markup: {}. Exception: {}".format(html_text, err)
            )
            TAG_RE = re.compile(r"<[^>]+>")
            return TAG_RE.sub(" ", html_text)
        # end of function
        return text.lower()

    def remove_accents(self, input_str, substitute=""):
        """Clean string from special characters.

        source: http://stackoverflow.com/a/5843560
        """
        return substitute.join(char for char in input_str if char.isalnum())

    def clean_xml(self, invalid_xml, mode="soft", substitute="_"):
        """Clean string of XML invalid characters.

        source: http://stackoverflow.com/a/13322581/2556577
        """
        # assumptions:
        #   doc = *( start_tag / end_tag / text )
        #   start_tag = '<' name *attr [ '/' ] '>'
        #   end_tag = '<' '/' name '>'
        ws = r"[ \t\r\n]*"  # allow ws between any token
        name = "[a-zA-Z]+"  # note: expand if necessary but the stricter the better
        attr = '{name} {ws} = {ws} "[^"]*"'  # note: fragile against missing '"'; no "'"
        start_tag = "< {ws} {name} {ws} (?:{attr} {ws})* /? {ws} >"
        end_tag = "{ws}".join(["<", "/", "{name}", ">"])
        tag = "{start_tag} | {end_tag}"

        assert "{{" not in tag
        while "{" in tag:  # unwrap definitions
            tag = tag.format(**vars())

        tag_regex = re.compile("(%s)" % tag, flags=re.VERBOSE)

        # escape &, <, > in the text
        iters = [iter(tag_regex.split(invalid_xml))] * 2
        pairs = zip_longest(*iters, fillvalue="")  # iterate 2 items at a time

        # get the clean version
        clean_version = "".join(escape(text) + tag for text, tag in pairs)
        if mode == "strict":
            clean_version = re.sub(r"<.*?>", substitute, clean_version)
        else:
            pass
        return clean_version


# ############################################################################
# #### Stand alone program ########
# #################################
if __name__ == "__main__":
    """standalone execution."""
    print("Stand-alone execution")
