#!/usr/bin/python
#
# This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Reporting: Declaration of the variables
#
# ****************************************************
installers = ["apex", "compass", "fuel", "joid"]

versions = ["master", "stable/colorado"]

# get data in the past 7 days
PERIOD = 7

# get the lastest 4 test results to determinate the success criteria
LASTEST_TESTS = 4

REPORTING_PATH = "."

URL_BASE = 'http://testresults.opnfv.org/test/api/v1/results'

# LOG_LEVEL = "ERROR"
LOG_LEVEL = "INFO"
LOG_FILE = REPORTING_PATH + "/reporting.log"
