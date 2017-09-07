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

import jinja2

import reporting.utils.reporting_utils as rp_utils
import reporting.utils.scenarioResult as sr

INSTALLERS = rp_utils.get_config('general.installers')
VERSIONS = rp_utils.get_config('general.versions')
PERIOD = rp_utils.get_config('general.period')

# Logger
LOGGER = rp_utils.getLogger("Bottlenecks-Status")
reportingDate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

LOGGER.info("*******************************************")
LOGGER.info("*   Generating reporting scenario status  *")
LOGGER.info("*   Data retention = %s days              *", PERIOD)
LOGGER.info("*                                         *")
LOGGER.info("*******************************************")

# retrieve the list of bottlenecks tests
BOTTLENECKS_TESTS = rp_utils.get_config('bottlenecks.test_list')
LOGGER.info("Bottlenecks tests: %s", BOTTLENECKS_TESTS)

# For all the versions
for version in VERSIONS:
    # For all the installers
    for installer in INSTALLERS:
        # get scenarios results data
        scenario_results = rp_utils.getScenarios("bottlenecks",
                                                 "posca_factor_ping",
                                                 installer,
                                                 version)
        LOGGER.info("scenario_results: %s", scenario_results)

        scenario_stats = rp_utils.getScenarioStats(scenario_results)
        LOGGER.info("scenario_stats: %s", scenario_stats)
        items = {}
        scenario_result_criteria = {}

        # From each scenarios get results list
        for s, s_result in scenario_results.items():
            LOGGER.info("---------------------------------")
            LOGGER.info("installer %s, version %s, scenario %s", installer,
                        version, s)
            ten_criteria = len(s_result)

            ten_score = 0
            for v in s_result:
                if "PASS" in v['criteria']:
                    ten_score += 1

            LOGGER.info("ten_score: %s / %s", (ten_score, ten_criteria))

            four_score = 0
            try:
                LASTEST_TESTS = rp_utils.get_config(
                    'general.nb_iteration_tests_success_criteria')
                s_result.sort(key=lambda x: x['start_date'])
                four_result = s_result[-LASTEST_TESTS:]
                LOGGER.debug("four_result: {}".format(four_result))
                LOGGER.debug("LASTEST_TESTS: {}".format(LASTEST_TESTS))
                # logger.debug("four_result: {}".format(four_result))
                four_criteria = len(four_result)
                for v in four_result:
                    if "PASS" in v['criteria']:
                        four_score += 1
                LOGGER.info("4 Score: %s / %s ", (four_score,
                                                  four_criteria))
            except Exception:
                LOGGER.error("Impossible to retrieve the four_score")

            try:
                s_status = (four_score * 100) / four_criteria
            except Exception:
                s_status = 0
            LOGGER.info("Score percent = %s", str(s_status))
            s_four_score = str(four_score) + '/' + str(four_criteria)
            s_ten_score = str(ten_score) + '/' + str(ten_criteria)
            s_score_percent = str(s_status)

            LOGGER.debug(" s_status: %s", s_status)
            if s_status == 100:
                LOGGER.info(">>>>> scenario OK, save the information")
            else:
                LOGGER.info(">>>> scenario not OK, last 4 iterations = %s, \
                             last 10 days = %s", (s_four_score, s_ten_score))

            s_url = ""
            if len(s_result) > 0:
                build_tag = s_result[len(s_result)-1]['build_tag']
                LOGGER.debug("Build tag: %s", build_tag)
                s_url = s_url = rp_utils.getJenkinsUrl(build_tag)
                LOGGER.info("last jenkins url: %s", s_url)

            # Save daily results in a file
            path_validation_file = ("./display/" + version +
                                    "/bottlenecks/scenario_history.txt")

            if not os.path.exists(path_validation_file):
                with open(path_validation_file, 'w') as f:
                    info = 'date,scenario,installer,details,score\n'
                    f.write(info)

            with open(path_validation_file, "a") as f:
                info = (reportingDate + "," + s + "," + installer +
                        "," + s_ten_score + "," +
                        str(s_score_percent) + "\n")
                f.write(info)

            scenario_result_criteria[s] = sr.ScenarioResult(s_status,
                                                            s_four_score,
                                                            s_ten_score,
                                                            s_score_percent,
                                                            s_url)

            LOGGER.info("--------------------------")

        templateLoader = jinja2.FileSystemLoader(".")
        templateEnv = jinja2.Environment(loader=templateLoader,
                                         autoescape=True)

        TEMPLATE_FILE = ("./reporting/bottlenecks/template"
                         "/index-status-tmpl.html")
        template = templateEnv.get_template(TEMPLATE_FILE)

        outputText = template.render(scenario_results=scenario_result_criteria,
                                     installer=installer,
                                     period=PERIOD,
                                     version=version,
                                     date=reportingDate)

        with open("./display/" + version +
                  "/bottlenecks/status-" + installer + ".html", "wb") as fh:
            fh.write(outputText)
