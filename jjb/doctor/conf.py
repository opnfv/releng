import datetime
import sys
import os

extensions = ['sphinx.ext.numfig']

# numfig:
number_figures = True
figure_caption_prefix = "Fig."

source_suffix = '.rst'
master_doc = 'index'
pygments_style = 'sphinx'
html_use_index = False

pdf_documents = [('index', u'Doctor', u'Doctor Project', u'OPNFV')]
pdf_fit_mode = "shrink"
pdf_stylesheets = ['sphinx','kerning','a4']
#latex_domain_indices = False
#latex_use_modindex = False
#latex_appendices = ['glossary', ]

_PREAMBLE = r"""
\usepackage{enumitem}
\setlistdepth{9}
\setlist[itemize,1]{label=$\bullet$}
\setlist[itemize,2]{label=$\bullet$}
\setlist[itemize,3]{label=$\bullet$}
\setlist[itemize,4]{label=$\bullet$}
\setlist[itemize,5]{label=$\bullet$}
\setlist[itemize,6]{label=$\bullet$}
\setlist[itemize,7]{label=$\bullet$}
\setlist[itemize,8]{label=$\bullet$}
\setlist[itemize,9]{label=$\bullet$}
\renewlist{itemize}{itemize}{9}
"""

latex_elements = {
    'printindex': '',
    'preamble': _PREAMBLE,
}

project = u'Doctor: Fault Management and Maintenance'
copyright = u'%s, OPNFV' % datetime.date.today().year
version = u'0.0.1'
release = u'0.0.1'
