# -*- coding: UTF-8 -*-
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
import unittest

# 3rd party
import semver
from validator_collection import validators

# module target
from elgeopaso import __about__

# #############################################################################
# ########## Classes ###############
# ##################################


class TestAbout(unittest.TestCase):
    """Test project metadata stored into the '__about__' module."""

    # -- Standard methods --------------------------------------------------------
    def setUp(self):
        """Executed before each test."""
        pass

    def tearDown(self):
        """Executed after each test."""
        pass

    # -- TESTS ---------------------------------------------------------
    def test_about(self):
        """Get project metadata"""
        self.assertIsInstance(__about__.__author__, str)
        self.assertIsInstance(__about__.__copyright__, str)
        self.assertIsInstance(__about__.__title__, str)
        self.assertTrue(semver.VersionInfo.isvalid(__about__.__version__))
        validators.email(__about__.__email__)
        validators.url(__about__.__uri__)


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    unittest.main()
