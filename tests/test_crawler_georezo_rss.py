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
from pathlib import Path
from sys import _getframe

# Django
from django.test import TestCase

# 3rd party
from validator_collection import validators

# module target
from elgeopaso.__about__ import __version__
from elgeopaso.jobs.crawlers import GeorezoRssParser

# #############################################################################
# ######## Globals #################
# ##################################


extension_pattern = "**/*.xml"


def get_test_marker():
    """Returns the module + function name to get a discriminator value."""
    return "{}__{}".format(Path(__file__).stem.upper(), _getframe(1).f_code.co_name)


# #############################################################################
# ########## Classes ###############
# ##################################


class TestCrawlerGeorezo(TestCase):
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
        georezo_parser.CRAWLER_LATEST_METADATA = "tests/fixtures/tmp/{}.json".format(
            get_test_marker()
        )

        # check
        validators.url(georezo_parser._build_feed_url())

        # parse feed and retrive new offers
        li_new_offers_to_add = georezo_parser.parse_new_offers()
        self.assertIsInstance(li_new_offers_to_add, list)

        # parse

    def test_load_rss(self):
        """Parse RSS samples."""
        for i in self.li_fixtures_repo:
            georezo_parser = GeorezoRssParser(
                feed_base_url=str(i.resolve()),
                items_to_parse=None,
                feed_length_param=None,
                user_agent="ElGeoPaso/{} https://elgeopaso.georezo.net/".format(
                    __version__
                ),
            )

            # enforce different metadata file path to avoid conflicts between tests and real process
            georezo_parser.CRAWLER_LATEST_METADATA = (
                "tests/fixtures/tmp/{}_{}.json".format(get_test_marker(), i.stem)
            )

            # parse feed and retrive new offers
            li_new_offers_to_add = georezo_parser.parse_new_offers(
                ignore_encoding_errors=False, only_new_offers=False
            )
            self.assertIsInstance(li_new_offers_to_add, list)

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


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    pass
