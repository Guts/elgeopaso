#!python3

"""
    Configuration for project documentation using Sphinx.
"""

import sys
from datetime import datetime

# standard library
from os import environ, path

sys.path.insert(0, path.abspath(".."))

# 3rd party
import django
import sphinx_rtd_theme  # noqa: F401 theme of Read the Docs

# Project
from elgeopaso import __about__

# -- Build environment -----------------------------------------------------
on_rtd = environ.get("READTHEDOCS", None) == "True"
environ["DJANGO_SETTINGS_MODULE"] = "elgeopaso.settings.local"
django.setup()

# -- Project information -----------------------------------------------------
author = __about__.__author__
copyright = __about__.__copyright__
description = __about__.__summary__
github_doc_root = __about__.__uri__ + "tree/master/docs"
project = __about__.__title__
version = release = __about__.__version__

# replacement variables
rst_epilog = ".. |title| replace:: %s" % project
rst_epilog += "\n.. |author| replace:: %s" % author
rst_epilog += "\n.. |repo_url| replace:: %s" % __about__.__uri__

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    # Sphinx included
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    # 3rd party
    "myst_parser",
    "sphinx_autodoc_typehints",
    "sphinx_copybutton",
    "sphinxext.opengraph",
    "sphinx_rtd_theme",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# source_suffix = ['.rst', '.md']
source_suffix = {".md": "markdown", ".rst": "restructuredtext"}
autosectionlabel_prefix_document = True
# The master toctree document.
master_doc = "index"

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "fr"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "samples/*", "Thumbs.db", ".DS_Store", "*env*", "libs/*"]


# -- Options for HTML output -------------------------------------------------

# html_favicon = "static/img/sqlitetoairtable_logo.svg"
# html_logo = "static/img/sqlitetoairtable_logo.svg"

# Ensure sidebar is the same along the pages
html_sidebars = {
    "**": ["globaltoc.html", "relations.html", "sourcelink.html", "searchbox.html"]
}
html_static_path = ["_static"]
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    # "canonical_url": __about__.__uri_homepage__,
    "display_version": True,
    "logo_only": False,
    "prev_next_buttons_location": "both",
    "style_external_links": True,
    "style_nav_header_background": "SteelBlue",
    # Toc options
    "collapse_navigation": False,
    "includehidden": False,
    "navigation_depth": 4,
    "sticky_navigation": False,
    "titles_only": False,
}


# Language to be used for generating the HTML full-text search index.
html_search_language = "fr"


# -- Options for extensions -------------------------------------------------

# -- EXTENSIONS --------------------------------------------------------

# -- intersphinx: refer to others sphinx docs
intersphinx_mapping = {
    "python": ("https://docs.python.org/fr/3/", None),
    "django": ("https://django.readthedocs.org/en/stable/", None),
}

# MyST Parser
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "dollarmath",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "substitution",
]

myst_substitutions = {
    "author": author,
    "date_update": datetime.now().strftime("%d %B %Y"),
    "description": description,
    "repo_url": __about__.__uri__,
    "title": project,
    "version": version,
}

myst_url_schemes = ("http", "https", "mailto")


# -- API autodoc
# run api doc
def run_apidoc(_):
    from sphinx.ext.apidoc import main

    cur_dir = path.normpath(path.dirname(__file__))
    output_path = path.join(cur_dir, "_apidoc")
    modules = path.normpath(path.join(cur_dir, "../elgeopaso"))
    exclusions = ["../.venv", "../tests"]
    main(["-e", "-f", "-M", "-o", output_path, modules] + exclusions)


# launch setup
def setup(app):
    app.connect("builder-inited", run_apidoc)
