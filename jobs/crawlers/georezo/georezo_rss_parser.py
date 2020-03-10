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
import logging
from datetime import timedelta
from pathlib import Path

# 3rd party modules
import arrow
import feedparser

FEEDPARSER_DOC_BASE_URL = "https://pythonhosted.org/feedparser/"

# ############################################################################
# ########## Classes #############
# ################################


class GeorezoRssParser:
    """Handy module to parse GeoRezo job offers through RSS."""

    def __init__(
        self,
        feed_base_url: str = "https://georezo.net/extern.php?fid=10",
        feed_length_param: str = "show",
        items_to_parse: int = 50,
        user_agent: str = "ElGeoPaso/DEV +https://elgeopaso.georezo.net/",
    ):
        # store parameters as attributes
        self.feed_base_url = feed_base_url
        self.feed_length_param = feed_length_param
        self.items_to_parse = items_to_parse
        self.user_agent = user_agent

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
    def get_previous_item_id(cls, from_source: str = "./last_id_georezo.txt") -> int:
        """Retrieve last parsed item ID from specified source.
        
        :param str from_source: where to load the ID. Defaults to: "./last_id_georezo.txt" - optional
        
        :raises NotImplementedError: [description]
        :raises ValueError: [description]

        :return: ID of the last parsed offer in the GeoRezo RSS
        :rtype: int
        """
        if from_source == "database":
            raise NotImplementedError
        elif Path(from_source).exists():
            logging.info(
                "Reading last parsed item ID from file: {}".format(from_source)
            )
            last_id_file = Path(from_source)
            # Get the id of the last offer parsed
            if last_id_file.exists():
                with last_id_file.open(mode="r") as in_file:
                    last_id = int(in_file.readline())
                logging.info("Previous offer ID: {}".format(last_id))
            else:
                logging.warning(
                    "File with the latest ID offer is missing: {}. "
                    "Considering latest ID = 0.".format(last_id_file.resolve())
                )
                last_id = 0
        else:
            raise ValueError

        return last_id

    def parse_new_offers(self):
        """Retrieve new offers from RSS feed."""
        last_id = self.get_previous_item_id() or 0

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
            agent=self.user_agent,
            # modified=True,
        )

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
                return offers_counter
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
                return offers_counter

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
            return offers_counter

        # looping on feed entries
        for entry in feed.entries:
            # get the ID cleaning 'link' markup
            try:
                job_id = int(entry.id.split("#")[1].lstrip("p"))
            except AttributeError as err:
                logging.error(
                    "Feed index corrupted: {} - ({})".format(
                        feed.entries.index(entry), err
                    )
                )
                continue

            # first offer parsed is the last published, so the biggest ID.
            # Put the ID in the dedicated text file.
            if feed.entries.index(entry) == 0:
                with last_id_file.open(mode="w") as out_file:
                    out_file.write(str(job_id))
            else:
                pass

            # formating publication date
            publication_date = arrow.get(entry.published, "ddd, D MMM YYYY HH:mm:ss Z")

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
    quicky = GeorezoRssParser()
    # print(dir(quicky))

    # quicky.get_previous_item_id()

    quicky.parse_new_offers()
