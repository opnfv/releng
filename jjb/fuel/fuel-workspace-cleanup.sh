#!/bin/bash
# @License Apache-2.0 <http://spdx.org/licenses/Apache-2.0>
##############################################################################
# Copyright (c) 2016 Ericsson AB and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
set -o errexit
set -o nounset
set -o pipefail

# delete the $WORKSPACE to open some space
/bin/rm -rf $WORKSPACE
