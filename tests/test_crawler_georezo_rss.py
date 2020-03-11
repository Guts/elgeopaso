# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""Usage from the repo root folder:

    .. code-block:: python

        # for whole test
        python -m unittest tests.test_crawler_georezo_rss

"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import unittest
from pathlib import Path

# 3rd party
from validator_collection import validators

# module target
from elgeopaso.__about__ import __version__
from jobs.crawlers import GeorezoRssParser

# #############################################################################
# ######## Globals #################
# ##################################

# variables
extension_pattern = "**/*.xml"

# #############################################################################
# ########## Classes ###############
# ##################################


class TestCrawlerGeorezo(unittest.TestCase):
    """Test crawler of GeoRezo RSS."""

    # -- Standard methods --------------------------------------------------------
    def setUp(self):
        """Executed before each test."""
        # fixtures
        self.tmp_fixtures_dir = Path("tests/fixtures/tmp/")
        self.tmp_fixtures_dir.mkdir(exist_ok=True)
        self.li_fixtures_repo = sorted(Path("tests/fixtures").glob(extension_pattern))

    def tearDown(self):
        """Executed after each test."""
        # clean fixtures
        for tmp_file in self.tmp_fixtures_dir.iterdir():
            tmp_file.unlink()

    # -- TESTS ---------------------------------------------------------
    def test_georezo_parser(self):
        """Test parser module."""
        # instanciate
        georezo_parser = GeorezoRssParser(
            items_to_parse=200,
            user_agent="ElGeoPaso/{} https://elgeopaso.georezo.net/".format(
                __version__
            ),
        )

        # enforce different metadata file path to avoid conflicts between tests and real process
        georezo_parser.CRAWLER_LATEST_METADATA = (
            "tests/fixtures/tmp/crawler_georezo_rss_latest_test.json"
        )

        # check
        validators.url(georezo_parser._build_feed_url())

        # parse feed and retrive new offers
        li_new_offers_to_add = georezo_parser.parse_new_offers()
        self.assertIsInstance(li_new_offers_to_add, list)

        # parse

    def test_load_rss(self):
        """Parse RSS sample"""
        for i in self.li_fixtures_repo:
            print(i.resolve())

    def test_id_extraction(self):
        """Extract ID from entry"""
        # raw string
        li_raw_str = [
            "https://georezo.net/forum/viewtopic.php?pid=331144#p331144",
            "<guid isPermaLink='true'>https://georezo.net/forum/viewtopic.php?pid=331081#p331081</guid>",
        ]

        for raw_str in li_raw_str:
            offer_id = GeorezoRssParser.extract_offer_id_from_url(raw_str)
            self.assertIsInstance(offer_id, int)
            # self.assertTrue(offer_id.isdigit())

        # using fixtures
        # for i in self.li_fixtures_repo:
        #     print(i.resolve())


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    unittest.main()
