# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('../'))
import easydev
# -- Project information -----------------------------------------------------

project = 'PyBluez'
copyright = '2004 - 2019, Albert Haung & contributors'
author = 'Albert Haung & contributors'

# The full version, including alpha/beta/rc tags
release = 'master'


# -- General configuration ---------------------------------------------------

master_doc = 'index'
# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'easydev.copybutton',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
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

# we are ignoring legacy for present while work is done on the files.
exclude_patterns = ['legacy']

# we use optional to indicate a function or method parameter is optional. Sphinx throws
# a warning in nitpick mode because option is not a python type recognised by intershpinx
# so we are hacking a workaround to stop the warning.

nitpick_ignore = [('py:class', 'optional')]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

html_theme_options = {
    'canonical_url': '',
    'analytics_id': '',  #  Provided by Google in your dashboard
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    # Toc options
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}

#enables the edit on github link
html_context = {
    "display_github": True, # Integrate GitHub
    "github_user": "pybluez", # Username
    "github_repo": "pybluez", # Repo name
    "github_version": "master", # Version
    "conf_py_path": "/docs/", # Path in the checkout to the docs root
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']


# Sphinx needs to import modules to read their docstrings and follows imports
# within files. Pybluez docs are built and published by CI on a linux box.
# So windows and macos specific modules need to be mocked.
autodoc_mock_imports = [
   'gattlib',
   'bluetooth._bluetooth',
   'fcntl', 
   'bluetooth._msbt', 
   'lightblue',
   '_widcomm'
  ]

# Generate file stubs. Set True if rebuilding API documentation.
autosummary_generate = False

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

#easydev.copybutton
extensions.append('easydev.copybutton')
jscopybutton_path = easydev.copybutton.get_copybutton_path()

if os.path.isdir('_static')==False:
    os.mkdir('_static')

import shutil
shutil.copy(jscopybutton_path, '_static')

html_static_path = ['_static']