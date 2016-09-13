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
import requests
import sys
import time
import yaml

import reportingUtils as utils
import reportingConf as conf
import scenarioResult as sr

# Logger
logger = utils.getLogger("Yardstick-Status")

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
        scenario_result_criteria = {}

        # From each scenarios get results list
        for s, s_result in scenario_results.items():
            logger.info("---------------------------------")
            logger.info("installer %s, version %s, scenario %s:" % (installer, version, s))

            s_status = 'KO'
            scenario_criteria = len(s_result)
            scenario_score = 0

            for v in s_result:
                if v['criteria'] == 'SUCCESS':
                    scenario_score += 1

            if scenario_score == scenario_criteria and scenario_criteria == 4:
                s_status = 'OK'
                logger.info(">>>>> scenario OK, save the information")
            else:
                logger.info(">>>> scenario not OK, score = %s/%s" % (scenario_score, scenario_criteria))

            s_score = str(scenario_score) + '/' + str(scenario_criteria)
            scenario_result_criteria[s] = sr.ScenarioResult(s_status, s_score)

            logger.info("--------------------------")

        templateLoader = jinja2.FileSystemLoader(conf.REPORTING_PATH)
        templateEnv = jinja2.Environment(loader=templateLoader)

        TEMPLATE_FILE = "/template/index-status-tmpl.html"
        template = templateEnv.get_template(TEMPLATE_FILE)

        outputText = template.render(scenario_results=scenario_result_criteria,
                                     installer=installer,
                                     period=conf.PERIOD,
                                     version=version)

        with open(conf.REPORTING_PATH + "/release/" + version +
                  "/index-status-" + installer + ".html", "wb") as fh:
            fh.write(outputText)
