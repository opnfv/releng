#!/usr/bin/python
#
# This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
import datetime
import jinja2
import os

# manage conf
import utils.reporting_utils as rp_utils

import utils.scenarioResult as sr

installers = rp_utils.get_config('general.installers')
versions = rp_utils.get_config('general.versions')
PERIOD = rp_utils.get_config('general.period')

# Logger
logger = rp_utils.getLogger("Storperf-Status")
reportingDate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

logger.info("*******************************************")
logger.info("*   Generating reporting scenario status  *")
logger.info("*   Data retention = %s days              *" % PERIOD)
logger.info("*                                         *")
logger.info("*******************************************")

# retrieve the list of storperf tests
storperf_tests = rp_utils.get_config('storperf.test_list')
logger.info("Storperf tests: %s" % storperf_tests)

# For all the versions
for version in versions:
    # For all the installers
    for installer in installers:
        # get scenarios results data
        # for the moment we consider only 1 case snia_steady_state
        scenario_results = rp_utils.getScenarios("snia_steady_state",
                                                 installer,
                                                 version)
        # logger.info("scenario_results: %s" % scenario_results)

        scenario_stats = rp_utils.getScenarioStats(scenario_results)
        logger.info("scenario_stats: %s" % scenario_stats)
        items = {}
        scenario_result_criteria = {}

        # From each scenarios get results list
        for s, s_result in scenario_results.items():
            logger.info("---------------------------------")
            logger.info("installer %s, version %s, scenario %s", installer,
                        version, s)
            ten_criteria = len(s_result)

            ten_score = 0
            for v in s_result:
                if "PASS" in v['criteria']:
                    ten_score += 1

            logger.info("ten_score: %s / %s" % (ten_score, ten_criteria))

            four_score = 0
            try:
                LASTEST_TESTS = rp_utils.get_config(
                    'general.nb_iteration_tests_success_criteria')
                s_result.sort(key=lambda x: x['start_date'])
                four_result = s_result[-LASTEST_TESTS:]
                logger.debug("four_result: {}".format(four_result))
                logger.debug("LASTEST_TESTS: {}".format(LASTEST_TESTS))
                # logger.debug("four_result: {}".format(four_result))
                four_criteria = len(four_result)
                for v in four_result:
                    if "PASS" in v['criteria']:
                        four_score += 1
                logger.info("4 Score: %s / %s " % (four_score,
                                                   four_criteria))
            except:
                logger.error("Impossible to retrieve the four_score")

            try:
                s_status = (four_score * 100) / four_criteria
            except:
                s_status = 0
            logger.info("Score percent = %s" % str(s_status))
            s_four_score = str(four_score) + '/' + str(four_criteria)
            s_ten_score = str(ten_score) + '/' + str(ten_criteria)
            s_score_percent = str(s_status)

            logger.debug(" s_status: {}".format(s_status))
            if s_status == 100:
                logger.info(">>>>> scenario OK, save the information")
            else:
                logger.info(">>>> scenario not OK, last 4 iterations = %s, \
                             last 10 days = %s" % (s_four_score, s_ten_score))

            s_url = ""
            if len(s_result) > 0:
                build_tag = s_result[len(s_result)-1]['build_tag']
                logger.debug("Build tag: %s" % build_tag)
                s_url = s_url = rp_utils.getJenkinsUrl(build_tag)
                logger.info("last jenkins url: %s" % s_url)

            # Save daily results in a file
            path_validation_file = ("./display/" + version +
                                    "/storperf/scenario_history.txt")

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

            logger.info("--------------------------")

        templateLoader = jinja2.FileSystemLoader(".")
        templateEnv = jinja2.Environment(loader=templateLoader,
                                         autoescape=True)

        TEMPLATE_FILE = "./reporting/storperf/template/index-status-tmpl.html"
        template = templateEnv.get_template(TEMPLATE_FILE)

        outputText = template.render(scenario_results=scenario_result_criteria,
                                     installer=installer,
                                     period=PERIOD,
                                     version=version,
                                     date=reportingDate)

        with open("./display/" + version +
                  "/storperf/status-" + installer + ".html", "wb") as fh:
            fh.write(outputText)
