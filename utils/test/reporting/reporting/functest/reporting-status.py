#!/usr/bin/python
#
# This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
import datetime
import os
import sys
import time

import jinja2

import reporting.functest.testCase as tc
import reporting.functest.scenarioResult as sr
import reporting.utils.reporting_utils as rp_utils

"""
Functest reporting status
"""

# Logger
LOGGER = rp_utils.getLogger("Functest-Status")

# Initialization
testValid = []
otherTestCases = []
reportingDate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

# init just connection_check to get the list of scenarios
# as all the scenarios run connection_check
healthcheck = tc.TestCase("connection_check", "functest", -1)

# Retrieve the Functest configuration to detect which tests are relevant
# according to the installer, scenario
cf = rp_utils.get_config('functest.test_conf')
period = rp_utils.get_config('general.period')
versions = rp_utils.get_config('general.versions')
installers = rp_utils.get_config('general.installers')
blacklist = rp_utils.get_config('functest.blacklist')
log_level = rp_utils.get_config('general.log.log_level')
exclude_noha = rp_utils.get_config('functest.exclude_noha')
exclude_virtual = rp_utils.get_config('functest.exclude_virtual')

functest_yaml_config = rp_utils.getFunctestConfig()

LOGGER.info("*******************************************")
LOGGER.info("*                                         *")
LOGGER.info("*   Generating reporting scenario status  *")
LOGGER.info("*   Data retention: %s days               *", period)
LOGGER.info("*   Log level: %s                         *", log_level)
LOGGER.info("*                                         *")
LOGGER.info("*   Virtual PODs exluded: %s              *", exclude_virtual)
LOGGER.info("*   NOHA scenarios excluded: %s           *", exclude_noha)
LOGGER.info("*                                         *")
LOGGER.info("*******************************************")

# Retrieve test cases of Tier 1 (smoke)
config_tiers = functest_yaml_config.get("tiers")

# we consider Tier 0 (Healthcheck), Tier 1 (smoke),2 (features)
# to validate scenarios
# Tier > 2 are not used to validate scenarios but we display the results anyway
# tricky thing for the API as some tests are Functest tests
# other tests are declared directly in the feature projects
for tier in config_tiers:
    if tier['order'] >= 0 and tier['order'] < 2:
        for case in tier['testcases']:
            if case['case_name'] not in blacklist:
                testValid.append(tc.TestCase(case['case_name'],
                                             "functest",
                                             case['dependencies']))
    elif tier['order'] == 2:
        for case in tier['testcases']:
            if case['case_name'] not in blacklist:
                otherTestCases.append(tc.TestCase(case['case_name'],
                                                  case['case_name'],
                                                  case['dependencies']))
    elif tier['order'] > 2:
        for case in tier['testcases']:
            if case['case_name'] not in blacklist:
                otherTestCases.append(tc.TestCase(case['case_name'],
                                                  "functest",
                                                  case['dependencies']))

LOGGER.debug("Functest reporting start")

# For all the versions
for version in versions:
    # For all the installers
    scenario_directory = "./display/" + version + "/functest/"
    scenario_file_name = scenario_directory + "scenario_history.txt"

    # check that the directory exists, if not create it
    # (first run on new version)
    if not os.path.exists(scenario_directory):
        os.makedirs(scenario_directory)

    # initiate scenario file if it does not exist
    if not os.path.isfile(scenario_file_name):
        with open(scenario_file_name, "a") as my_file:
            LOGGER.debug("Create scenario file: %s", scenario_file_name)
            my_file.write("date,scenario,installer,detail,score\n")

    for installer in installers:

        # get scenarios
        scenario_results = rp_utils.getScenarios("functest",
                                                 "connection_check",
                                                 installer,
                                                 version)
        # get nb of supported architecture (x86, aarch64)
        architectures = rp_utils.getArchitectures(scenario_results)
        LOGGER.info("Supported architectures: %s", architectures)

        for architecture in architectures:
            LOGGER.info("Architecture: %s", architecture)
            # Consider only the results for the selected architecture
            # i.e drop x86 for aarch64 and vice versa
            filter_results = rp_utils.filterArchitecture(scenario_results,
                                                         architecture)
            scenario_stats = rp_utils.getScenarioStats(filter_results)
            items = {}
            scenario_result_criteria = {}

            # in case of more than 1 architecture supported
            # precise the architecture
            installer_display = installer
            if "fuel" in installer:
                installer_display = installer + "@" + architecture

            # For all the scenarios get results
            for s, s_result in filter_results.items():
                LOGGER.info("---------------------------------")
                LOGGER.info("installer %s, version %s, scenario %s:",
                            installer, version, s)
                LOGGER.debug("Scenario results: %s", s_result)

                # Green or Red light for a given scenario
                nb_test_runnable_for_this_scenario = 0
                scenario_score = 0
                # url of the last jenkins log corresponding to a given
                # scenario
                s_url = ""
                if len(s_result) > 0:
                    build_tag = s_result[len(s_result)-1]['build_tag']
                    LOGGER.debug("Build tag: %s", build_tag)
                    s_url = rp_utils.getJenkinsUrl(build_tag)
                    if s_url is None:
                        s_url = "http://testresultS.opnfv.org/reporting"
                    LOGGER.info("last jenkins url: %s", s_url)
                testCases2BeDisplayed = []
                # Check if test case is runnable / installer, scenario
                # for the test case used for Scenario validation
                try:
                    # 1) Manage the test cases for the scenario validation
                    # concretely Tiers 0-3
                    for test_case in testValid:
                        test_case.checkRunnable(installer, s,
                                                test_case.getConstraints())
                        LOGGER.debug("testcase %s (%s) is %s",
                                     test_case.getDisplayName(),
                                     test_case.getName(),
                                     test_case.isRunnable)
                        time.sleep(1)
                        if test_case.isRunnable:
                            name = test_case.getName()
                            displayName = test_case.getDisplayName()
                            project = test_case.getProject()
                            nb_test_runnable_for_this_scenario += 1
                            LOGGER.info(" Searching results for case %s ",
                                        displayName)
                            if "fuel" in installer:
                                result = rp_utils.getCaseScoreFromBuildTag(
                                    name,
                                    s_result)
                            else:
                                result = rp_utils.getCaseScore(name, installer,
                                                               s, version)
                            # if no result set the value to 0
                            if result < 0:
                                result = 0
                            LOGGER.info(" >>>> Test score = " + str(result))
                            test_case.setCriteria(result)
                            test_case.setIsRunnable(True)
                            testCases2BeDisplayed.append(tc.TestCase(name,
                                                                     project,
                                                                     "",
                                                                     result,
                                                                     True,
                                                                     1))
                            scenario_score = scenario_score + result

                    # 2) Manage the test cases for the scenario qualification
                    # concretely Tiers > 3
                    for test_case in otherTestCases:
                        test_case.checkRunnable(installer, s,
                                                test_case.getConstraints())
                        LOGGER.debug("testcase %s (%s) is %s",
                                     test_case.getDisplayName(),
                                     test_case.getName(),
                                     test_case.isRunnable)
                        time.sleep(1)
                        if test_case.isRunnable:
                            name = test_case.getName()
                            displayName = test_case.getDisplayName()
                            project = test_case.getProject()
                            LOGGER.info(" Searching results for case %s ",
                                        displayName)
                            if "fuel" in installer:
                                result = rp_utils.getCaseScoreFromBuildTag(
                                    name,
                                    s_result)
                            else:
                                result = rp_utils.getCaseScore(name, installer,
                                                               s, version)
                            # at least 1 result for the test
                            if result > -1:
                                test_case.setCriteria(result)
                                test_case.setIsRunnable(True)
                                testCases2BeDisplayed.append(tc.TestCase(
                                    name,
                                    project,
                                    "",
                                    result,
                                    True,
                                    4))
                            else:
                                LOGGER.debug("No results found")

                        items[s] = testCases2BeDisplayed
                except Exception:  # pylint: disable=broad-except
                    LOGGER.error("Error installer %s, version %s, scenario %s",
                                 installer, version, s)
                    LOGGER.error("No data available: %s", sys.exc_info()[0])

                # **********************************************
                # Evaluate the results for scenario validation
                # **********************************************
                # the validation criteria = nb runnable tests x 3
                # because each test case can get
                # 0 point (never PASS)
                # 1 point at least (PASS once over the time window)
                # 2 points (PASS more than once but 1 FAIL on the last 4)
                # 3 points PASS on the last 4 iterations
                # e.g. 1 scenario = 10 cases
                # 1 iteration : max score = 10 (10x1)
                # 2 iterations : max score = 20 (10x2)
                # 3 iterations : max score = 20
                # 4 or more iterations : max score = 30 (1x30)
                LOGGER.info("Number of iterations for this scenario: %s",
                            len(s_result))
                if len(s_result) > 3:
                    k_score = 3
                elif len(s_result) < 2:
                    k_score = 1
                else:
                    k_score = 2

                scenario_criteria = nb_test_runnable_for_this_scenario*k_score

                # score for reporting
                s_score = str(scenario_score) + "/" + str(scenario_criteria)
                s_score_percent = rp_utils.getScenarioPercent(
                    scenario_score,
                    scenario_criteria)

                s_status = "KO"
                if scenario_score < scenario_criteria:
                    LOGGER.info(">>>> scenario not OK, score = %s/%s",
                                scenario_score, scenario_criteria)
                    s_status = "KO"
                else:
                    LOGGER.info(">>>>> scenario OK, save the information")
                    s_status = "OK"
                    path_validation_file = ("./display/" + version +
                                            "/functest/" +
                                            "validated_scenario_history.txt")
                    with open(path_validation_file, "a") as f:
                        time_format = "%Y-%m-%d %H:%M"
                        info = (datetime.datetime.now().strftime(time_format) +
                                ";" + installer_display + ";" + s + "\n")
                        f.write(info)

                # Save daily results in a file
                with open(scenario_file_name, "a") as f:
                    info = (reportingDate + "," + s + "," + installer_display +
                            "," + s_score + "," +
                            str(round(s_score_percent)) + "\n")
                    f.write(info)

                scenario_result_criteria[s] = sr.ScenarioResult(
                    s_status,
                    s_score,
                    s_score_percent,
                    s_url)
                LOGGER.info("--------------------------")

            templateLoader = jinja2.FileSystemLoader(".")
            templateEnv = jinja2.Environment(
                loader=templateLoader, autoescape=True)

            TEMPLATE_FILE = ("./reporting/functest/template"
                             "/index-status-tmpl.html")
            template = templateEnv.get_template(TEMPLATE_FILE)

            outputText = template.render(
                scenario_stats=scenario_stats,
                scenario_results=scenario_result_criteria,
                items=items,
                installer=installer_display,
                period=period,
                version=version,
                date=reportingDate)

            with open("./display/" + version +
                      "/functest/status-" +
                      installer_display + ".html", "wb") as fh:
                fh.write(outputText)

            LOGGER.info("Manage export CSV & PDF")
            rp_utils.export_csv(scenario_file_name, installer_display, version)
            LOGGER.error("CSV generated...")

            # Generate outputs for export
            # pdf
            url_pdf = rp_utils.get_config('general.url')
            pdf_path = ("./display/" + version +
                        "/functest/status-" + installer_display + ".html")
            pdf_doc_name = ("./display/" + version +
                            "/functest/status-" + installer_display + ".pdf")
            rp_utils.export_pdf(pdf_path, pdf_doc_name)
            LOGGER.info("PDF generated...")
