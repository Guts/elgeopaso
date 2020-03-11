# -*- coding: UTF-8 -*-
#! python3  # noqa: E265

"""
    Name:         GeoRezo Jobs RSS Parser
    Purpose:      Parse GeoRezo RSS
    Python:       3.7+
"""

# ##############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import json
import logging
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, urlparse

# 3rd party modules
import arrow
import feedparser

# ############################################################################
# ########## GLOBALS #############
# ################################

# Feed base URL
FEEDPARSER_DOC_BASE_URL = "https://pythonhosted.org/feedparser/"

# ############################################################################
# ########## Classes #############
# ################################


class GeorezoRssParser:
    """Handy module to parse GeoRezo job offers through RSS.

    :param str feed_base_url: URL to the feed. Defaults to: "https://georezo.net/extern.php?fid=10" - optional
    :param str feed_length_param: name of the URL parameter to specifiy the number of items. Defaults to: "show" - optional
    :param int items_to_parse: number of items to request to the feed. Defaults to: 50 - optional
    :param str user_agent: HTTP user-agent. Defaults to: "ElGeoPaso/DEV +https://elgeopaso.georezo.net/" - optional
    """

    # Attributes

    # Feed datetime structure
    # see: https://docs.python.org/fr/3/library/datetime.html#strftime-and-strptime-format-codes
    FEED_DATETIME_RAW_FORMAT = "%a, %d %b %Y %H:%M:%S %z"
    FEED_DATETIME_RAW_FORMAT_ARROW = "ddd, D MMM YYYY HH:mm:ss Z"

    # File to store the feed metadata
    CRAWLER_LATEST_METADATA = "crawler_georezo_rss_latest.json"

    def __init__(
        self,
        feed_base_url: str = "https://georezo.net/extern.php?fid=10",
        feed_length_param: str = "show",
        items_to_parse: int = 50,
        user_agent: str = "ElGeoPaso/DEV +https://elgeopaso.georezo.net/",
    ):
        """Instanciate the class."""
        # store parameters as attributes
        self.feed_base_url = feed_base_url
        self.feed_length_param = feed_length_param
        self.items_to_parse = items_to_parse

        # set user agent to global feedparser
        # see: https://pythonhosted.org/feedparser/http-useragent.html
        feedparser.USER_AGENT = user_agent

    def _build_feed_url(self) -> str:
        """Build RSS feed URL from class attributes.

        :return: RSS feed URL with parameters
        :rtype: str
        """
        if self.feed_length_param and self.items_to_parse:
            complete_feed_url = "{}&{}={}".format(
                self.feed_base_url, self.feed_length_param, self.items_to_parse
            )
        else:
            complete_feed_url = self.feed_base_url

        logging.debug("Feed URL built: {}".format(complete_feed_url))
        return complete_feed_url

    @classmethod
    def extract_offer_id_from_url(cls, in_url: str) -> int:
        """Parse input URL to extract RSS item ID = job offer ID.

        :param str in_url: input URL as string. In GeoRezo RSS, it's:
          - in raw XML: '<guid isPermaLink="true">https://georezo.net/forum/viewtopic.php?pid=331081#p331081</guid>'
          - parsed by feedparser: entry.id = 'https://georezo.net/forum/viewtopic.php?pid=331144#p331144'

        :return: offer ID
        :rtype: int
        """
        parsed_url = urlparse(in_url)
        parsed_query = parse_qs(parsed_url.query)

        extracted_offer_id = parsed_query.get("pid")
        logging.debug(
            "Offer ID extracted: {} from URL '{}'".format(extracted_offer_id, in_url)
        )

        # keep only digits
        extracted_offer_id = "".join(i for i in extracted_offer_id if i.isdigit())

        return int(extracted_offer_id)

    @classmethod
    def load_previous_crawler_metadata(
        cls, from_source: str = "./last_id_georezo.txt"
    ) -> dict:
        """Retrieve last parsed item ID from specified source.

        :param str from_source: where to load the ID. Defaults to: "./last_id_georezo.txt"

        :raises NotImplementedError: [description]
        :raises ValueError: [description]

        :return: dictionary with previous crawler execution metadata
        :rtype: dict
        """
        in_source = Path(from_source)
        if in_source.exists() and in_source.suffix == ".json":
            logging.info(
                "Reading last parsed item ID from file: {}".format(from_source)
            )
            with in_source.open("r") as in_json:
                out_dict = json.load(in_json)
        elif in_source.exists() and in_source.suffix == ".txt":
            logging.info(
                "Reading last parsed item ID from file: {}".format(from_source)
            )
            last_id_file = Path(from_source)
            # Get the id of the last offer parsed
            with last_id_file.open(mode="r") as in_file:
                last_id = int(in_file.readline())
            logging.info("Previous offer ID: {}".format(last_id))
            out_dict = {"latest_offer_id": last_id}

        else:
            logging.warning(
                "File with the latest ID offer is missing: {}. "
                "Considering latest ID = 0.".format(last_id_file.resolve())
            )
            out_dict = {"latest_offer_id": 0}

        return out_dict

    def save_parsing_metadata(
        self, feed_parsed: feedparser.FeedParserDict, save_type: str = "json"
    ) -> dict:
        """Dumps some metadata from parsed feed to track behavior and enforce future \
            usage into a structured JSON file.

        :param feedparser.FeedParserDict feed_parsed: parsed feed
        :param str save_type: type of save to perform. Defaults to: "json" - optional

        :return: dictionary of saved data
        :rtype: dict

        :example:

        .. code-block:: json

            [
                {
                    "encoding": "ISO-8859-1",
                    "entries_required": 50,
                    "entries_total": 50,
                    "feed_updated_converted": "2020-03-10 13:07:06+01:00",
                    "feed_updated_parsed": [
                        2020,
                        3,
                        10,
                        12,
                        7,
                        6,
                        1,
                        70,
                        0
                    ],
                    "feed_updated_raw": "Tue, 10 Mar 2020 13:07:06 +0100",
                    "latest_offer_id": 331132,
                    "status": 200,
                    "version": "rss20"
                }
            ]
        """
        # extract last job offer id
        if len(feed_parsed.entries):
            last_job_offer_id = self.extract_offer_id_from_url(feed_parsed.entries[0].id)
        else:
            logging.warning("Unable to retrive latest job offer ID")
            last_job_offer_id = 0

        # convert datetime to str
        try:
            feed_build_dt = datetime.strptime(
                feed_parsed.feed.updated, self.FEED_DATETIME_RAW_FORMAT,
            )
        except Exception as err:
            logging.error(
                "Feed date '{}' can be parsed with format: {}. Error: {}".format(
                    feed_parsed.feed.updated, self.FEED_DATETIME_RAW_FORMAT, err
                )
            )
            # fallback value
            feed_build_dt = None

        # dump data
        if save_type == "json":
            data_to_save = {
                "feed_updated_raw": feed_parsed.feed.updated,
                "feed_updated_converted": str(feed_build_dt),
                "feed_updated_parsed": feed_parsed.feed.updated_parsed,
                "entries_required": self.items_to_parse,
                "entries_total": len(feed_parsed.entries),
                "encoding": feed_parsed.encoding,
                "latest_offer_id": last_job_offer_id,
                "status": feed_parsed.status,
                "version": feed_parsed.version,
            }

            json_dest = Path(self.CRAWLER_LATEST_METADATA)
            with json_dest.open("w") as json_file:
                json.dump(data_to_save, json_file, indent=2, sort_keys=True)

            return data_to_save

    def parse_new_offers(self, ignore_encoding_errors: bool = True) -> list:
        """Retrieve new offers from RSS feed.

        :param bool ignore_encoding_errors: option to ignore encoding exceptions. Defaults to: True

        :return: list
        :rtype: list
        """
        previous_metadata = (
            self.load_previous_crawler_metadata(self.CRAWLER_LATEST_METADATA) or 0
        )
        last_id = previous_metadata.get("latest_offer_id")

        # list to store offers IDs
        li_new_job_offers_id = []

        # reset offers counter
        offers_counter = 0

        # RSS parser
        logging.info(
            "Connecting to the RSS. Expecting {} entries as specified in settings.".format(
                self.items_to_parse
            )
        )
        feed = feedparser.parse(
            url_file_stream_or_string=self._build_feed_url(),
            # modified=True,
        )
        self.save_parsing_metadata(feed)

        # test if feed is well-formed
        # https://pythonhosted.org/feedparser/bozo.html#bozo-detection
        if feed.bozo:
            logging.warning("Parser raised a non blocking error. Investigating...")
            if isinstance(feed.bozo_exception, feedparser.CharacterEncodingOverride):
                feedparser_related_doc = "{}character-encoding.html#handling-incorrectly-declared-encodings".format(
                    FEEDPARSER_DOC_BASE_URL
                )
                logging.error(
                    "Feed encoding is badly declared. It could be parsed but with errors."
                    " Parser error: {}."
                    " See: {}".format(feed.bozo_exception, feedparser_related_doc)
                )
                if not ignore_encoding_errors:
                    return li_new_job_offers_id
            elif isinstance(feed.bozo_exception, feedparser.CharacterEncodingUnknown):
                feedparser_related_doc = "{}character-encoding.html#handling-incorrectly-declared-encodings".format(
                    FEEDPARSER_DOC_BASE_URL
                )
                logging.error(
                    "Feed encoding could not be identified. "
                    "Parsing result is likely to be unpredictable..."
                    " Parser error: {}."
                    " See: {}".format(feed.bozo_exception, feedparser_related_doc)
                )
                if not ignore_encoding_errors:
                    return li_new_job_offers_id

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
            return li_new_job_offers_id

        # looping on feed entries
        for entry in feed.entries:
            # get the ID cleaning 'link' markup
            try:
                job_id = self.extract_offer_id_from_url(entry.id)
            except AttributeError as err:
                logging.error(
                    "Feed index corrupted: {} - ({})".format(
                        feed.entries.index(entry), err
                    )
                )
                continue

            # if entry's ID is greater than ID stored into the file,
            # that means the offer is more recent and has to be processed
            if job_id > last_id:
                # incrementing counter
                offers_counter += 1
                # adding offer's ID to the list of new offers to process
                li_new_job_offers_id.append(job_id)
                logging.debug("New offer added: {}".format(job_id))
            else:
                logging.debug(
                    "Offer ID inferior to the last registered: {}".format(job_id)
                )
                continue

        # if new offers => launch next processes
        if offers_counter > 0:
            logging.info("{} new offers to add.".format(len(li_new_job_offers_id)))
        else:
            logging.info("No new offer retrieved...")

        return li_new_job_offers_id


# #############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """Standalone execution for quick and dirty use or test"""
    quicky = GeorezoRssParser(items_to_parse=1)
    # print(dir(quicky))

    # print(quicky.load_previous_crawler_metadata())
    # print(quicky.load_previous_crawler_metadata(quicky.CRAWLER_LATEST_METADATA))

    quicky.parse_new_offers()
