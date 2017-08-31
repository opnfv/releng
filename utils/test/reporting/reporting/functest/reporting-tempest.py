#!/usr/bin/env python

# Copyright (c) 2017 Orange and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
# SPDX-license-identifier: Apache-2.0

from datetime import datetime
import json
import os

from urllib2 import Request, urlopen, URLError
import jinja2

import reporting.utils.reporting_utils as rp_utils

INSTALLERS = rp_utils.get_config('general.installers')
ITEMS = ["tests", "Success rate", "duration"]

CURRENT_DIR = os.getcwd()

PERIOD = rp_utils.get_config('general.period')
CRITERIA_NB_TEST = 100
CRITERIA_DURATION = 1800
CRITERIA_SUCCESS_RATE = 100

logger = rp_utils.getLogger("Tempest")
logger.info("************************************************")
logger.info("*   Generating reporting Tempest_smoke_serial  *")
logger.info("*   Data retention = %s days                   *", PERIOD)
logger.info("*                                              *")
logger.info("************************************************")

logger.info("Success criteria:")
logger.info("nb tests executed > %s s ", CRITERIA_NB_TEST)
logger.info("test duration < %s s ", CRITERIA_DURATION)
logger.info("success rate > %s ", CRITERIA_SUCCESS_RATE)

# For all the versions
for version in rp_utils.get_config('general.versions'):
    for installer in INSTALLERS:
        # we consider the Tempest results of the last PERIOD days
        url = ("http://" + rp_utils.get_config('testapi.url') +
               "?case=tempest_smoke_serial&period=" + str(PERIOD) +
               "&installer=" + installer + "&version=" + version)
        request = Request(url)
        logger.info(("Search tempest_smoke_serial results for installer %s"
                     " for version %s"), installer, version)
        try:
            response = urlopen(request)
            k = response.read()
            results = json.loads(k)
        except URLError as err:
            logger.error("Error code: %s", err)
        logger.debug("request sent: %s", url)
        logger.debug("Results from API: %s", results)
        test_results = results['results']
        logger.debug("Test results: %s", test_results)
        scenario_results = {}
        criteria = {}
        errors = {}

        for r in test_results:
            # Retrieve all the scenarios per installer
            # In Brahmaputra use version
            # Since Colorado use scenario
            if not r['scenario'] in scenario_results.keys():
                scenario_results[r['scenario']] = []
            scenario_results[r['scenario']].append(r)

        logger.debug("Scenario results: %s", scenario_results)

        for s, s_result in scenario_results.items():
            scenario_results[s] = s_result[0:5]
            # For each scenario, we build a result object to deal with
            # results, criteria and error handling
            for result in scenario_results[s]:
                result["start_date"] = result["start_date"].split(".")[0]
                logger.debug("start_date= %s", result["start_date"])

                # retrieve results
                # ****************
                nb_tests_run = result['details']['tests']
                nb_tests_failed = result['details']['failures']
                logger.debug("nb_tests_run= %s", nb_tests_run)
                logger.debug("nb_tests_failed= %s", nb_tests_failed)

                try:
                    success_rate = (100 * (int(nb_tests_run) -
                                           int(nb_tests_failed)) /
                                    int(nb_tests_run))
                except ZeroDivisionError:
                    success_rate = 0

                result['details']["tests"] = nb_tests_run
                result['details']["Success rate"] = str(success_rate) + "%"

                logger.info("nb_tests_run= %s", result['details']["tests"])
                logger.info("test rate = %s",
                            result['details']["Success rate"])

                # Criteria management
                # *******************
                crit_tests = False
                crit_rate = False
                crit_time = False

                # Expect that at least 165 tests are run
                if nb_tests_run >= CRITERIA_NB_TEST:
                    crit_tests = True

                # Expect that at least 90% of success
                if success_rate >= CRITERIA_SUCCESS_RATE:
                    crit_rate = True

                # Expect that the suite duration is inferior to 30m
                stop_date = datetime.strptime(result['stop_date'],
                                              '%Y-%m-%d %H:%M:%S')
                start_date = datetime.strptime(result['start_date'],
                                               '%Y-%m-%d %H:%M:%S')

                delta = stop_date - start_date

                if delta.total_seconds() < CRITERIA_DURATION:
                    crit_time = True

                result['criteria'] = {'tests': crit_tests,
                                      'Success rate': crit_rate,
                                      'duration': crit_time}
                try:
                    logger.debug("Nb Test run: %s", nb_tests_run)
                    logger.debug("Test duration: %s", delta)
                    logger.debug("Success rate: %s", success_rate)
                except Exception:  # pylint: disable=broad-except
                    logger.error("Data format error")

                # Error management
                # ****************
                try:
                    errors = result['details']['errors']
                    logger.info("errors: %s", errors)
                    result['errors'] = errors
                except Exception:  # pylint: disable=broad-except
                    logger.error("Error field not present (Brahamputra runs?)")

        templateLoader = jinja2.FileSystemLoader(".")
        templateEnv = jinja2.Environment(loader=templateLoader,
                                         autoescape=True)

        TEMPLATE_FILE = "./reporting/functest/template/index-tempest-tmpl.html"
        template = templateEnv.get_template(TEMPLATE_FILE)

        outputText = template.render(scenario_results=scenario_results,
                                     items=ITEMS,
                                     installer=installer)

        with open("./display/" + version +
                  "/functest/tempest-" + installer + ".html", "wb") as fh:
            fh.write(outputText)
logger.info("Tempest automatic reporting succesfully generated.")
