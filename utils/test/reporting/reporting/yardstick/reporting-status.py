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

import utils.scenarioResult as sr
from scenarios import config as cf

# manage conf
import utils.reporting_utils as rp_utils

installers = rp_utils.get_config('general.installers')
versions = rp_utils.get_config('general.versions')
PERIOD = rp_utils.get_config('general.period')

# Logger
logger = rp_utils.getLogger("Yardstick-Status")
reportingDate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

logger.info("*******************************************")
logger.info("*   Generating reporting scenario status  *")
logger.info("*   Data retention = %s days              *" % PERIOD)
logger.info("*                                         *")
logger.info("*******************************************")


# For all the versions
for version in versions:
    # For all the installers
    for installer in installers:
        # get scenarios results data
        scenario_results = rp_utils.getScenarioStatus(installer, version)
        if 'colorado' == version:
            stable_result = rp_utils.getScenarioStatus(installer,
                                                       'stable/colorado')
            for k, v in stable_result.items():
                if k not in scenario_results.keys():
                    scenario_results[k] = []
                scenario_results[k] += stable_result[k]
        scenario_result_criteria = {}

        for s in scenario_results.keys():
            if installer in cf.keys() and s in cf[installer].keys():
                scenario_results.pop(s)

        # From each scenarios get results list
        for s, s_result in scenario_results.items():
            logger.info("---------------------------------")
            logger.info("installer %s, version %s, scenario %s", installer,
                        version, s)

            ten_criteria = len(s_result)
            ten_score = 0
            for v in s_result:
                ten_score += v

            LASTEST_TESTS = rp_utils.get_config(
                'general.nb_iteration_tests_success_criteria')
            four_result = s_result[:LASTEST_TESTS]
            four_criteria = len(four_result)
            four_score = 0
            for v in four_result:
                four_score += v

            s_status = str(rp_utils.get_percent(four_result, s_result))
            s_four_score = str(four_score) + '/' + str(four_criteria)
            s_ten_score = str(ten_score) + '/' + str(ten_criteria)
            s_score_percent = rp_utils.get_percent(four_result, s_result)

            if '100' == s_status:
                logger.info(">>>>> scenario OK, save the information")
            else:
                logger.info(">>>> scenario not OK, last 4 iterations = %s, \
                            last 10 days = %s" % (s_four_score, s_ten_score))

            # Save daily results in a file
            path_validation_file = ("./display/" + version +
                                    "/yardstick/scenario_history.txt")

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
                                                            s_score_percent)

            logger.info("--------------------------")

        templateLoader = jinja2.FileSystemLoader(".")
        templateEnv = jinja2.Environment(loader=templateLoader,
                                         autoescape=True)

        TEMPLATE_FILE = "./reporting/yardstick/template/index-status-tmpl.html"
        template = templateEnv.get_template(TEMPLATE_FILE)

        outputText = template.render(scenario_results=scenario_result_criteria,
                                     installer=installer,
                                     period=PERIOD,
                                     version=version,
                                     date=reportingDate)

        with open("./display/" + version +
                  "/yardstick/status-" + installer + ".html", "wb") as fh:
            fh.write(outputText)
