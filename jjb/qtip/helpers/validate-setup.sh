#!/usr/bin/env bash
##############################################################################
# Copyright (c) 2017 ZTE and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

set -e

# setup virtualenv
sudo pip install -u virtualenv virtualenvwrapper
export WORKON_HOME=$HOME/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh
mkvirtualenv qtip
workon qtip

# setup qtip
sudo pip install $HOME/repos/qtip

# testing
qtip --version
qtip --help
