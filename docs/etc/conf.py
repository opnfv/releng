'''
Base configuration file for building OPNFV docs

You can override this configuration by putting 'conf.py' in the document
directory (e.g. docs/how-to-use-docs/conf.py). If there is no 'conf.py'
in the document directory, this file will be copied to that directory
before the document builder jobs ('opnfv-docs-verify' and 'opnfv-docs-merge').

See https://wiki.opnfv.org/documentation/tools .
'''

# NOTE: You may need python package installation for new sphinx extension.
#       Install python package with 'pip' in you machine, and ask OPNFV
#       releng team to make sure that the package is installed in the infra.
extensions = ['sphinxcontrib.httpdomain']

needs_sphinx = '1.3'
master_doc = 'index'
pygments_style = 'sphinx'

html_use_index = False
numfig = True
html_logo = 'opnfv-logo.png'

latex_domain_indices = False
latex_logo = 'opnfv-logo.png'
