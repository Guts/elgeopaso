# -*- coding: utf-8 -*-
#! python3  # noqa: E265  # noqa: E265

"""
    Metadata bout the package to easily retrieve informations about it.
    See: https://packaging.python.org/guides/single-sourcing-package-version/
"""

from datetime import date

__all__ = [
    "__title__",
    "__summary__",
    "__uri__",
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "__copyright__",
]


__author__ = "Julien M. (guts@github)"
__copyright__ = "2018 - {0}, {1}".format(date.today().year, __author__)
__email__ = "elpaso@georezo.net"
__license__ = "GNU Lesser General Public License v3.0"
__summary__ = (
    "Simple web application performing statistical analisis on job offers "
    "published on GeoRezo."
)
__title__ = "El Géo Paso"
__title_clean__ = "".join(e for e in __title__ if e.isalnum())
__uri__ = "https://github.com/Guts/elgeopaso/"
__version__ = "1.0.0"
__version_info__ = tuple(
    [
        int(num) if num.isdigit() else num
        for num in __version__.replace("-", ".", 1).split(".")
    ]
)
