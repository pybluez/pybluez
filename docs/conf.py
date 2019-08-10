# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath('../'))
on_rtd = os.environ.get('READTHEDOCS', None) == 'True'
import setup as _setup

# -- Project information -----------------------------------------------------

project = _setup.__project__.title()
copyright = '2004-{} {}'.format(datetime.now().year, _setup.__author__)
author = _setup.__author__
version = _setup.__version__
release = _setup.__version__


# -- General configuration ---------------------------------------------------

master_doc = 'index'
# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.coverage', 
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'recommonmark'
   ]


# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# we use optional to indicate a function or method parameter is optional. Sphinx throws
# a warning in nitpick mode because option is not a python type recognised by intershpinx
# so we are hacking a workaround to stop the warning.

nitpick_ignore = [('py:class', 'optional')]

# -- Options for HTML output -------------------------------------------------

if on_rtd:
    html_theme = 'sphinx_rtd_theme'
    #html_theme_options = {}
    #html_sidebars = {}
else:
    html_theme = 'sphinx_rtd_theme'
    #html_theme_options = {}
    #html_sidebars = {}
html_title = '%s %s Documentation' % (project, version)
#html_theme_path = []
#html_short_title = None
#html_logo = None
#html_favicon = None
html_static_path = ['_static']
#html_extra_path = []
#html_last_updated_fmt = '%b %d, %Y'
#html_use_smartypants = True
#html_additional_pages = {}
#html_domain_indices = True
#html_use_index = True
#html_split_index = False
#html_show_sourcelink = True
#html_show_sphinx = True
#html_show_copyright = True
#html_use_opensearch = ''
#html_file_suffix = None
htmlhelp_basename = '%sdoc' % _setup.__project__

# Hack to make wide tables work properly in RTD
# See https://github.com/snide/sphinx_rtd_theme/issues/117 for details
#def setup(app):
#    app.add_stylesheet('style_override.css')


html_static_path = ['_static']


# Sphinx needs to import modules to read their docstrings and follows imports
# within files. Pybluez docs are built and published by CI on a linux box.
# So windows and macos specific modules need to be mocked.
autodoc_mock_imports = [
    'bluetooth._bluetooth',
    'bluetooth._msbt',
  ]

# Napoleon is a sphinx extension allowing autodoc to parse docstrings which don't follow
# restructured text formatting rules. It will currently attempt to parse google and numpy
# styles.
#  
# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True

# intersphinx
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None)
    }