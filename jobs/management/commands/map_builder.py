# -*- coding: utf-8 -*-
#! python3  # noqa: E265

# ############################################################################
# ########## Libraries #############
# ##################################
# Standard library
import gzip
import json
import logging
from concurrent.futures import as_completed, ThreadPoolExecutor
from pathlib import Path
from tempfile import NamedTemporaryFile

# Django
from django.conf import settings
from django.core.management.base import BaseCommand
from django.templatetags.static import static

# 3rd party
import requests

# Django project
from elgeopaso.__about__ import __title_clean__
from jobs.models import Offer

# ############################################################################
# ########### Classes #############
# #################################


class Command(BaseCommand):
    args = "<foo bar ...>"
    help = """
                Commands to generate geojson files used for map visualization.
           """

    # -- CLI ------------------------------------------------------
    def handle(self, *args, **options):
        """Download required files and launch GeoJSON build."""
        # test settings
        if not isinstance(settings.GEOJSON_FOLDER, Path):
            logging.error(
                TypeError(
                    "GeoJSON folder is not a correct path: {}".format(
                        settings.GEOJSON_FOLDER
                    )
                )
            )
            return
        else:
            geojson_dir = settings.GEOJSON_FOLDER

        # download required files
        self.external_downloader()

        # build GeoJSON for French departements
        for i in geojson_dir.iterdir():
            if i.stem == "fr_departements":
                self.build_geojson_fr_departements(in_geojson=i)

    # -- DOWNLOAD ----------------------------------------------------------------------
    def build_geojson_fr_departements(self, in_geojson: Path):
        """Parse input GeoJSON and update needed values to display maps.

        :param Path in_geojson: Path to the input GeoJSON
        """
        # vars
        years = [i.year for i in Offer.objects.dates("pub_date", "year")]
        # load input geojson
        if not in_geojson.exists():
            logging.error("Input GeoJSON doesn't exists: {}".format(in_geojson))
            return in_geojson

        with in_geojson.open("r", encoding="utf8") as data_file:
            data = json.load(data_file)

        # prepare metrics
        offers_dpts = Offer.objects.filter(place__scale__exact="DEPARTEMENT")

        # parsing
        for feat in data.get("features"):
            props = feat.get("properties")
            dpt_offers = offers_dpts.filter(place__code=props.get("code"))
            props["JOBS_TOTAL"] = dpt_offers.count()
            for y in years:
                props["JOBS_{}".format(y)] = dpt_offers.filter(pub_date__year=y).count()
                props["histo"] = [
                    {
                        "values": [
                            {
                                "x": year,
                                "y": dpt_offers.filter(pub_date__year=year).count(),
                            }
                            for year in years
                        ],
                        "key": "Offres",
                        "color": "#decbe4",
                    }
                ]
        # Save file
        out_gjson_fr_dpts = in_geojson.parent / "{}{}".format(
            in_geojson.stem, "_jobs.geojson"
        )
        with out_gjson_fr_dpts.open("w", encoding="utf8") as jsonFile:
            json.dump(data, jsonFile, ensure_ascii=False)

        logging.info(
            "GeoJSON completed with French departements statistics updated: {}".format(
                out_gjson_fr_dpts
            )
        )
        return out_gjson_fr_dpts

    # -- DOWNLOAD ----------------------------------------------------------------------
    def external_downloader(self, overwrite: bool = False) -> list:
        """Download external files.

        :param bool overwrite: option to overwrite existing files. Defaults to: False - optional

        :return: list of downloaded files
        :rtype: list
        """
        # variables
        geojson_dir = settings.GEOJSON_FOLDER
        li_url_to_dl = []  # list of tuple (url, path where dowload the file)

        # filter on files to download
        for k, v in settings.GEOJSON_TO_DOWLOAD.items():
            final_path = geojson_dir / "{}.geojson".format(k)
            if final_path.exists() and not overwrite:
                logging.info(
                    "File already exists: {}. Ignoring the download.".format(final_path)
                )
            else:
                logging.info(
                    "File doesn't exists or overwrite is enabled: {}. "
                    "Let's download it.".format(final_path)
                )
                li_url_to_dl.append((v, final_path))

        # if no file to download, exit method
        if not len(li_url_to_dl):
            logging.info("No file to download.")
            return li_url_to_dl

        # or launch download of files
        with ThreadPoolExecutor() as executor:
            # Start the load operations and mark each future with its URL
            future_to_url = {
                executor.submit(
                    self.url_to_file, url=target[0], final_file=target[1]
                ): target
                for target in li_url_to_dl
            }
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    data = future.result()
                except Exception as exc:
                    logging.error("%r generated an exception: %s" % (url, exc))
                else:
                    logging.info("%r page is %s bytes" % (url, data))

    def url_to_file(self, url: str, final_file: Path, timeout: int = 60):
        """Download file from URL to local storage.

        Source: https://stackoverflow.com/a/16696317/2556577

        :param str url: [description]
        :param Path final_file: [description]
        :param int timeout: [description]. Defaults to: 60 - optional
        """
        # download file into a temporary file
        with requests.get(url, stream=True, allow_redirects=True) as r:
            r.raise_for_status()
            with final_file.open("wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
                        # free memory usage
                        f.flush()

        return f.name


# ############################################################################
# #### Stand alone program ########
# #################################
if __name__ == "__main__":
    """standalone execution."""
    # logging with debug
    logging.basicConfig(level=logging.DEBUG)
