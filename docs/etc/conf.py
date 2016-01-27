# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2016 Linux Foundation and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
'''
Base configuration file for building OPNFV docs

You can override this configuration by putting 'conf.py' in the document
directory (e.g. docs/how-to-use-docs/conf.py). If there is no 'conf.py'
in the document directory, this file will be copied to that directory
before the document builder jobs ('opnfv-docs-verify' and 'opnfv-docs-merge').

You may need python package installation for new sphinx extension.
Install python package with 'pip' in your machine and add the extension to
the 'extensions' list below to test the documentation build locally.
If you feel that your extensions would be useful for other projects too,
we encourage you to propose a change in the releng repository.

For further guidance see the https://wiki.opnfv.org/documentation/tools page.
'''

extensions = ['sphinxcontrib.httpdomain',
              'sphinx.ext.autodoc',
              'sphinx.ext.viewcode',
              'sphinx.ext.napoleon']

needs_sphinx = '1.3'
master_doc = 'index'
pygments_style = 'sphinx'

html_use_index = False
numfig = True
html_logo = 'opnfv-logo.png'

latex_domain_indices = False
latex_logo = 'opnfv-logo.png'
