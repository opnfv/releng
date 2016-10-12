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

import reportingUtils as utils
import reportingConf as conf
import scenarioResult as sr
from scenarios import config as cf

# Logger
logger = utils.getLogger("Yardstick-Status")
reportingDate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

logger.info("*******************************************")
logger.info("*   Generating reporting scenario status  *")
logger.info("*   Data retention = %s days              *" % conf.PERIOD)
logger.info("*                                         *")
logger.info("*******************************************")


# For all the versions
for version in conf.versions:
    # For all the installers
    for installer in conf.installers:
        # get scenarios results data
        scenario_results = utils.getScenarioStatus(installer, version)
        if 'colorado' == version:
            stable_result = utils.getScenarioStatus(installer,
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
            logger.info("installer %s, version %s, scenario %s:" % (installer,
                                                                    version, s))

            ten_criteria = len(s_result)
            ten_score = 0
            for v in s_result:
                ten_score += v

            four_result = s_result[:conf.LASTEST_TESTS]
            four_criteria = len(four_result)
            four_score = 0
            for v in four_result:
                four_score += v

            s_status = str(utils.get_percent(four_result, s_result))
            s_four_score = str(four_score) + '/' + str(four_criteria)
            s_ten_score = str(ten_score) + '/' + str(ten_criteria)
            s_score_percent = utils.get_percent(four_result, s_result)

            if '100' == s_status:
                logger.info(">>>>> scenario OK, save the information")
            else:
                logger.info(">>>> scenario not OK, last 4 iterations = %s, \
                            last 10 days = %s" % (s_four_score, s_ten_score))

            # Save daily results in a file
            path_validation_file = (conf.REPORTING_PATH +
                                    "/release/" + version +
                                    "/scenario_history.txt")

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

        templateLoader = jinja2.FileSystemLoader(conf.REPORTING_PATH)
        templateEnv = jinja2.Environment(loader=templateLoader, autoescape=True)

        TEMPLATE_FILE = "/template/index-status-tmpl.html"
        template = templateEnv.get_template(TEMPLATE_FILE)

        outputText = template.render(scenario_results=scenario_result_criteria,
                                     installer=installer,
                                     period=conf.PERIOD,
                                     version=version,
                                     date=reportingDate)

        with open(conf.REPORTING_PATH + "/release/" + version +
                  "/index-status-" + installer + ".html", "wb") as fh:
            fh.write(outputText)
