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
from pathlib import Path
from sys import _getframe

# Django
from django.core.management import call_command
from django.test import TestCase

# module target
from elgeopaso.utils import TextToolbelt
from elgeopaso.jobs.analyzer import GeorezoOfferAnalizer
from elgeopaso.jobs.analyzer.georezo.parsers import ContentParser, TitleParser
from elgeopaso.jobs.models import Place

# fixtures
from .fixtures.offers_titles import LI_FIXTURES_OFFERS_TITLE

# #############################################################################
# ######## Globals #################
# ##################################

# vars
extension_pattern = "**/*.xml"
txt_toolbelt = TextToolbelt()


def get_test_marker():
    """Returns the module + function name to get a discriminator value."""
    return "{}__{}".format(Path(__file__).stem.upper(), _getframe(1).f_code.co_name)


# #############################################################################
# ########## Classes ###############
# ##################################


class TestAnalizerGeorezo(TestCase):
    """Test crawler of GeoRezo RSS."""

    # -- Standard methods --------------------------------------------------------
    def setUp(self):
        """Executed before each test."""
        # populate database for analisis
        call_command("loaddata", "elgeopaso/jobs/fixtures/contracts.json", verbosity=0)
        call_command("loaddata", "elgeopaso/jobs/fixtures/jobs.json", verbosity=0)
        call_command("loaddata", "elgeopaso/jobs/fixtures/places.json", verbosity=0)
        call_command("loaddata", "elgeopaso/jobs/fixtures/technos.json", verbosity=0)
        call_command("loaddata", "elgeopaso/jobs/fixtures/sources.json", verbosity=0)

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
    def test_title_cleaner(self):
        """Test special characters removal in title."""
        for i in LI_FIXTURES_OFFERS_TITLE:
            clean_title = txt_toolbelt.remove_html_markups(html_text=i.raw_title)
            self.assertIsInstance(clean_title, str)

    def test_map_builder(self):
        """Test map_builder command management"""
        call_command("map_builder", verbosity=0)

    def test_place_extraction(self):
        """Test extraction of place from title."""
        # instanciate
        analyser = GeorezoOfferAnalizer(li_offers_ids=["11111",])

        # fixtures
        for i in LI_FIXTURES_OFFERS_TITLE:
            # clean title
            analyser.offer_id = LI_FIXTURES_OFFERS_TITLE.index(i)
            clean_title = txt_toolbelt.remove_html_markups(i.raw_title)

            # title parser
            title_parser = TitleParser(analyser.offer_id, clean_title)

            result_place = title_parser.parse_place()

            if i.well_formed:
                self.assertIsInstance(result_place, Place)
                self.assertEqual(result_place.code, i.expected_place_code)
                self.assertEqual(result_place.name, i.expected_place_name)
                self.assertEqual(result_place.scale, i.expected_place_scale)
            else:
                self.assertIsInstance(result_place, str)

    # def test_contract_type(self):
    #     """Test extraction of contract type from title."""
    #     # instanciate
    #     analyser = GeorezoOfferAnalizer(li_offers_ids=["11111",])

    #     # fixtures
    #     for i in LI_FIXTURES_OFFERS_TITLE:
    #         analyser.offer_id = i.raw_title
    #         result = analyser.parse_contract_type(i.raw_title)

    #         if i.well_formed:
    #             self.assertIsInstance(result, Place)
    #             self.assertEqual(result.code, i.expected_place_code)
    #             self.assertEqual(result.name, i.expected_place_name)
    #             self.assertEqual(result.scale, i.expected_place_scale)
    #         else:
    #             self.assertIsInstance(result, str)


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    pass
