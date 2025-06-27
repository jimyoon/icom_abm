# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('..'))

# -- Project information -----------------------------------------------------

project = 'CHANCE-C'
copyright = '2024, Battelle Memorial Institute'
author = 'Jim Yoon, Chris R. Vernon'
release = '0.1.0'

# The full version, including alpha/beta/rc tags
version = '0.1.0'

# The master toctree document.
master_doc = 'index'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.mathjax',
    'sphinx.ext.githubpages',
    'sphinx.ext.autosummary',
    'pydata_sphinx_theme',
    'myst_parser',
    'nbsphinx',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['build', 'Thumbs.db', '.DS_Store']

# The suffix of source filenames.
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'pydata_sphinx_theme'

# Theme options for pydata-sphinx-theme
html_theme_options = {
    "github_url": "https://github.com/jimyoon/icom_abm",
    "show_toc_level": 2,
    "logo": {
        "image_light": "_static/chance-c-logo.png",
        "image_dark": "_static/chance-c-logo.png",
        "text": "CHANCE-C",
    },
    "navbar_align": "left",
    "navbar_start": ["navbar-logo"],
    "navbar_center": ["navbar-nav"],
    "navbar_end": ["navbar-icon-links"],
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/jimyoon/icom_abm",
            "icon": "fab fa-github-square",
        },
    ],
    "secondary_sidebar_items": ["page-toc", "edit-this-page", "sourcelink"],
    "announcement": "🚀 CHANCE-C v0.1.0 is now available! Check out the tutorials to get started.",
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
html_sidebars = {
    '**': [
        'globaltoc.html',
        'relations.html',
        'sourcelink.html',
        'searchbox.html',
    ]
}

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
html_logo = "_static/chance-c-logo.png"

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
# html_favicon = "_static/favicon.ico"

# -- Options for autodoc ----------------------------------------------------

# Automatically extract typehints when specified and place them in
# descriptions of the relevant function/method.
autodoc_typehints = 'description'

# Don't show typehints in the signature
autodoc_typehints_format = 'short'

# Don't show the module name in the signature
add_module_names = False

# Include private methods
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__',
    'show-inheritance': True,
    'inherited-members': True,
}

# -- Options for intersphinx mapping ----------------------------------------

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
    'geopandas': ('https://geopandas.org/en/stable/', None),
    'matplotlib': ('https://matplotlib.org/stable/', None),
}

# -- Options for Napoleon extension -----------------------------------------

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = True
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_use_keyword = True
napoleon_custom_sections = None

# -- Options for MyST-Parser ------------------------------------------------

myst_enable_extensions = [
    "amsmath",
    "colon_fence",
    "deflist",
    "dollarmath",
    "html_image",
    "html_admonition",
    "replacements",
    "smartquotes",
    "substitution",
    "tasklist",
]

# -- Options for HTMLHelp output -------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'CHANCE-Cdoc'

# -- Options for LaTeX output ----------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    'papersize': 'a4paper',

    # The font size ('10pt', '11pt' or '12pt').
    'pointsize': '11pt',

    # Additional stuff for the LaTeX preamble.
    'preamble': r'''
        \usepackage{charter}
        \usepackage[defaultsans]{lato}
        \usepackage{inconsolata}
    ''',

    # Latex figure (float) alignment
    'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'CHANCE-C.tex', 'CHANCE-C Documentation',
     'CHANCE-C Development Team', 'manual'),
]

# -- Options for manual page output -----------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'chance-c', 'CHANCE-C Documentation',
     [author], 1)
]

# -- Options for Texinfo output ---------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'CHANCE-C', 'CHANCE-C Documentation',
     author, 'CHANCE-C', 'Coastal Hazards And Neighborhood Change - Computational',
     'Miscellaneous'),
]

# -- Options for Epub output -------------------------------------------------

# Bibliographic Dublin Core info.
epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
epub_identifier = 'https://github.com/jimyoon/icom_abm'

# A unique identification for the text.
epub_uid = 'CHANCE-C-1.0.0'

# A list of files that should not be packed into the epub file.
epub_exclude_files = ['search.html']

# -- Extension configuration -------------------------------------------------

# Mock imports for packages that might not be available during build
autodoc_mock_imports = [
    'gdal',
    'ogr',
    'proj',
    'geos',
    'fiona',
    'shapely',
    'pyproj',
    'rtree',
    'pynsim',
    'geopandas',
    'geopandas.geoseries',
    'geopandas.base',
    'geopandas._compat',
    'geopandas._config',
    'packaging.version',
]

# Suppress warnings for failed imports
autodoc_docstring_signature = True
autodoc_preserve_defaults = True

# Skip modules that cause import errors
# autodoc_skip_member = lambda app, what, name, obj, skip, options: skip or name.startswith('_')

# (Removed setup(app) function that added autodoc_mock_imports)

autosummary_generate = True  # Automatically generate autosummary stub pages

# -- Options for nbsphinx ---------------------------------------------------

# Execute notebooks when building docs
# Options: 'always', 'never', 'auto'
# 'auto' will execute notebooks that don't have outputs
nbsphinx_execute = 'never'  # Set to 'always' to execute notebooks during build

# Allow errors in notebook execution
nbsphinx_allow_errors = True

# Timeout for notebook execution (in seconds)
nbsphinx_timeout = 300

# Kernel to use for notebook execution
nbsphinx_kernel_name = 'python3'

# Custom CSS for better notebook formatting
nbsphinx_codecell_lexer = 'ipython3'

# Exclude input/output prompts from notebooks
nbsphinx_prolog = """
{% set docname = env.doc2path(env.docname, base=None) %}
{% set notebook_name = docname.split('/')[-1] %}
{% if notebook_name == "custom_simulations.ipynb" %}
    {% set actual_notebook = "custom.ipynb" %}
{% else %}
    {% set actual_notebook = notebook_name %}
{% endif %}

.. note::

   This page was generated from a Jupyter notebook.
   Interactive online version: 
   :download:`Download notebook <../../../notebooks/{{ actual_notebook }}>`
"""

# Epilog for notebooks
nbsphinx_epilog = """
----

**Note:** This tutorial is also available as an interactive Jupyter notebook in the ``notebooks/`` directory of the CHANCE-C repository.
""" 