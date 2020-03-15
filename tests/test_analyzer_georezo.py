# -*- coding: utf-8 -*-
#! python3  # noqa E265

"""Usage from the repo root folder:

    .. code-block:: python

        # for whole test
        python manage.py test tests.test_analyzer_georezo

"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import unittest
from pathlib import Path
from sys import _getframe

# module target
from jobs.analyzer import Analizer
from jobs.models import Place

# fixtures
from .fixtures.offers_titles import LI_FIXTURES_OFFERS_TITLE

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


class TestAnalizerGeorezo(unittest.TestCase):
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
    def test_place_extraction(self):
        """Test extration of place from title."""
        # instanciate
        analyser = Analizer(li_offers_ids=["11111",])

        # fixtures
        for i in LI_FIXTURES_OFFERS_TITLE:
            analyser.offer_id = i.raw_title
            result_place = analyser.parse_place(i.raw_title)

            if i.well_formed:
                self.assertIsInstance(result_place, Place)
                self.assertEqual(result_place.code, i.expected_place_code)
                self.assertEqual(result_place.name, i.expected_place_name)
                self.assertEqual(result_place.scale, i.expected_place_scale)
            else:
                self.assertIsInstance(result_place, str)


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    unittest.main()
