# coding: utf-8
#! python3  # noqa: E265

"""
    Job offers fixtures to test against project analisis mechanisms.
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
from typing import NamedTuple

# ##############################################################################
# ########## Classes ###############
# ##################################
class OfferFixture(NamedTuple):
    """Model of offer to be tested."""

    raw_title: str
    well_formed: bool
    # contract type
    expected_contract_type: str
    # place
    expected_place_name: str
    expected_place_code: str
    expected_place_scale: str


# ##############################################################################
# ########## Fixtures ##############
# ##################################
LI_FIXTURES_OFFERS_TITLE = [
    OfferFixture(
        raw_title="[CDD] Administrateur(trice) Bases de donnees - Haute Loire (43)",
        well_formed=True,
        expected_contract_type="CDD",
        expected_place_code="43",
        expected_place_name="Haute-Loire",
        expected_place_scale="DEPARTEMENT",
    ),
    OfferFixture(
        raw_title="[CDD 18 mois] Charge(e) de mission – Base de donnees (22)",
        well_formed=True,
        expected_contract_type="CDD",
        expected_place_code="22",
        expected_place_name="Côtes-d'Armor",
        expected_place_scale="DEPARTEMENT",
    ),
    OfferFixture(
        raw_title="[CDI] Administrateurˇtrice base donnees spatiales - Besancon (25)",
        well_formed=True,
        expected_contract_type="CDI",
        expected_place_code="",
        expected_place_name="",
        expected_place_scale="",
    ),
    OfferFixture(
        raw_title="[APPRENT] Offre de DRT 'Maquette 3D et usages' - (38)",
        well_formed=True,
        expected_contract_type="APPRENTISSAGE",
        expected_place_code="38",
        expected_place_name="Isère",
        expected_place_scale="DEPARTEMENT",
    ),
    OfferFixture(
        raw_title="Développeur - Ile de France",
        well_formed=False,
        expected_contract_type="CDI",
        expected_place_code="99",
        expected_place_name="Doubs",
        expected_place_scale="DEPARTEMENT",
    ),
    OfferFixture(
        raw_title="[FP ou contract.] Technicien supérieur géomaticien - STIF (75)",
        well_formed=True,
        expected_contract_type="FPT",
        expected_place_code="75",
        expected_place_name="Paris",
        expected_place_scale="DEPARTEMENT",
    ),
]
