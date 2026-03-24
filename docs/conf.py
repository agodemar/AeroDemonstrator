"""Sphinx configuration for AeroDemonstrator documentation."""

import os
import shutil
import sys

# Add source directory to path for autodoc
sys.path.insert(0, os.path.abspath('../src'))

# Copy notebooks into the docs source tree so nbsphinx can process them.
# A symlink would cause Sphinx's symlink-resolving path logic to compute
# incorrect relative paths for notebook output images.
_notebooks_src = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'notebooks'))
_notebooks_dst = os.path.join(os.path.dirname(__file__), 'notebooks')
if os.path.isdir(_notebooks_src):
    if os.path.isdir(_notebooks_dst):
        shutil.rmtree(_notebooks_dst)
    shutil.copytree(_notebooks_src, _notebooks_dst)

# -- Project information ------------------------------------------------
project = 'AeroDemonstrator'
copyright = '2024, AeroDemonstrator Contributors'
author = 'AeroDemonstrator Contributors'
release = '0.1.0'
version = '0.1'

# -- General configuration ----------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.mathjax',
    'myst_parser',
    'nbsphinx',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Source file suffixes
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# -- Options for HTML output -------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_theme_options = {
    'navigation_depth': 4,
    'titles_only': False,
    'logo_only': False,
}

# -- Options for autodoc -----------------------------------------------
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'show-inheritance': True,
}
autodoc_typehints = 'description'

# -- Options for Napoleon ----------------------------------------------
napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True

# -- Options for intersphinx -------------------------------------------
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable', None),
    'scipy': ('https://docs.scipy.org/doc/scipy', None),
    'matplotlib': ('https://matplotlib.org/stable', None),
}

# -- Options for MathJax -----------------------------------------------
mathjax_path = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js'

# -- Options for nbsphinx -------------------------------------------------
# Use pre-computed cell outputs; do not re-execute notebooks during the build
nbsphinx_execute = 'never'

