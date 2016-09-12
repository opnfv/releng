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
# list of test cases declared in testcases.yaml but that must not be
# taken into account for the scoring
blacklist = ["ovno", "security_scan", 'odl-sfc']
# versions = ["brahmaputra", "master"]
versions = ["master", "colorado"]
PERIOD = 50
MAX_SCENARIO_CRITERIA = 50
# get the last 5 test results to determinate the success criteria
NB_TESTS = 5
# REPORTING_PATH = "/usr/share/nginx/html/reporting/functest"
REPORTING_PATH = "."
URL_BASE = 'testresults.opnfv.org/test/api/v1/results'
TEST_CONF = "https://git.opnfv.org/cgit/functest/plain/ci/testcases.yaml"
LOG_LEVEL = "ERROR"
LOG_FILE = REPORTING_PATH + "/reporting.log"
