#! python3  # noqa E265

"""Usage from the repo root folder:

    .. code-block:: python

        # for whole test
        python -m unittest tests.test_about

"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
from datetime import datetime
import unittest

# 3rd party
import arrow

# module
from elgeopaso.jobs.crawlers import GeorezoRssParser

# #############################################################################
# ########## Classes ###############
# ##################################


class TestDatetimesParsing(unittest.TestCase):
    """Test different datetimes parsing used along the project."""

    # -- Standard methods --------------------------------------------------------
    def setUp(self):
        """Executed before each test."""
        pass

    def tearDown(self):
        """Executed after each test."""
        pass

    # -- TESTS ---------------------------------------------------------
    def test_rss_datetimes(self):
        """Datetimes within RSS"""
        # raw datetime extracted from the XML
        rss_dt_updated_raw = "Mon, 09 Mar 2020 09:42:07 +0100"
        # datetime returned by feedparser
        # see: https://pythonhosted.org/feedparser/reference-feed-updated_parsed.html
        rss_dt_updated_parsed = "2020-03-09T21:00:29+00:00"

        # using standard lib
        datetime.strptime(rss_dt_updated_raw, GeorezoRssParser.FEED_DATETIME_RAW_FORMAT)

        # using arrow
        arrow.get(rss_dt_updated_raw, GeorezoRssParser.FEED_DATETIME_RAW_FORMAT_ARROW)
        arrow.get(rss_dt_updated_parsed)


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    unittest.main()
