# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
sys.path.insert(0, os.path.abspath('../../src'))

project = 'CRISP GUI'
copyright = '2025, Lewis Dean & Robin de Freitas'
author = 'Lewis Dean & Robin de Freitas'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',               # Automatically extract documentation from docstrings
    'sphinx.ext.napoleon',              # Support Google and NumPy style docstrings
    'sphinx_autodoc_typehints',         # Include type hints in documentation
]


templates_path = ['_templates']
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
html_title = "CRISP Documentation"

html_theme_options = {
    'logo': 'images/logo.png',
    'description': 'Sphinx auto-documentation for the CRISP backend codebase.',
}

