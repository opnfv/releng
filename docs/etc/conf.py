'''
Base configuration file for sphinx-build.

You can override this configuration by putting 'conf.py' in the document
directory (e.g. how-to-use-docs/conf.py).
'''

import datetime

needs_sphinx = '1.3'
master_doc = 'index'
pygments_style = 'sphinx'

html_use_index = False
numfig = True
html_logo = '../etc/opnfv-logo.png'

latex_elements = {'printindex': ''}
latex_logo = '../etc/opnfv-logo.png'

copyright = u'%s, OPNFV' % datetime.date.today().year
version = u'1.0.0'
release = u'1.0.0'
