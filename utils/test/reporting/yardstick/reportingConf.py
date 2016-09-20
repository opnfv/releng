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

versions = ["master", "colorado"]

# get data in the past 10 days
PERIOD = 10

# get the lastest 4 test results to determinate the success criteria
LASTEST_TESTS = 4

REPORTING_PATH = "."

URL_BASE = 'http://testresults.opnfv.org/test/api/v1/results'
TEST_CONF = "https://git.opnfv.org/cgit/yardstick/plain/tests/ci/report_config.yaml"

# LOG_LEVEL = "ERROR"
LOG_LEVEL = "INFO"
LOG_FILE = REPORTING_PATH + "/reporting.log"
