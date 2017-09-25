#!/usr/bin/python
#
# This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
"""
vIMS reporting status
"""
from urllib2 import Request, urlopen, URLError
import json
import jinja2

import reporting.utils.reporting_utils as rp_utils

LOGGER = rp_utils.getLogger("vIMS")

PERIOD = rp_utils.get_config('general.period')
VERSIONS = rp_utils.get_config('general.versions')
URL_BASE = rp_utils.get_config('testapi.url')

LOGGER.info("****************************************")
LOGGER.info("*   Generating reporting vIMS          *")
LOGGER.info("*   Data retention = %s days           *", PERIOD)
LOGGER.info("*                                      *")
LOGGER.info("****************************************")

INSTALLERS = rp_utils.get_config('general.installers')
STEP_ORDER = ["initialisation", "orchestrator", "vnf", "test_vnf"]
LOGGER.info("Start vIMS reporting processing....")

# For all the versions
for version in VERSIONS:
    for installer in INSTALLERS:

        # get nb of supported architecture (x86, aarch64)
        # get scenarios
        scenario_results = rp_utils.getScenarios("functest",
                                                 "cloudify_ims",
                                                 installer,
                                                 version)

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

            LOGGER.info("Search vIMS results for installer: %s, version: %s",
                        installer, version)
            request = Request("http://" + URL_BASE + '?case=cloudify_ims&'
                              'installer=' + installer + '&version=' + version)
            try:
                response = urlopen(request)
                k = response.read()
                results = json.loads(k)
            except URLError as err:
                LOGGER.error("Error code: %s", err)

            test_results = results['results']

            # LOGGER.debug("Results found: %s" % test_results)

            scenario_results = {}
            for r in test_results:
                if not r['scenario'] in scenario_results.keys():
                    scenario_results[r['scenario']] = []
                scenario_results[r['scenario']].append(r)

            # LOGGER.debug("scenario result: %s" % scenario_results)

            for s, s_result in scenario_results.items():
                scenario_results[s] = s_result[0:5]
                for result in scenario_results[s]:
                    try:
                        format_result = result['details']['test_vnf']['result']

                        # round durations of the different steps
                        result['details']['orchestrator']['duration'] = round(
                            result['details']['orchestrator']['duration'], 1)
                        result['details']['vnf']['duration'] = round(
                            result['details']['vnf']['duration'], 1)
                        result['details']['test_vnf']['duration'] = round(
                            result['details']['test_vnf']['duration'], 1)

                        res_orch = \
                            result['details']['orchestrator']['duration']
                        res_vnf = result['details']['vnf']['duration']
                        res_test_vnf = \
                            result['details']['test_vnf']['duration']
                        res_signaling = \
                            result['details']['test_vnf']['result']['failures']

                        # Manage test result status
                        if res_signaling != 0:
                            LOGGER.debug("At least 1 signalig test FAIL")
                            result['details']['test_vnf']['status'] = "FAIL"
                        else:
                            LOGGER.debug("All signalig tests PASS")
                            result['details']['test_vnf']['status'] = "PASS"

                        LOGGER.debug("Scenario %s, Installer %s",
                                     s_result[1]['scenario'], installer)
                        LOGGER.debug("Orchestrator deployment: %ss", res_orch)
                        LOGGER.debug("vIMS deployment: %ss", res_vnf)
                        LOGGER.debug("VNF testing: %ss", res_test_vnf)
                        LOGGER.debug("VNF testing results: %s", format_result)
                    except Exception as err:  # pylint: disable=broad-except
                        LOGGER.error("Uncomplete data %s", err)
                    LOGGER.debug("----------------------------------------")

        templateLoader = jinja2.FileSystemLoader(".")
        templateEnv = jinja2.Environment(loader=templateLoader,
                                         autoescape=True)

        TEMPLATE_FILE = "./reporting/functest/template/index-vims-tmpl.html"
        template = templateEnv.get_template(TEMPLATE_FILE)

        outputText = template.render(scenario_results=scenario_results,
                                     step_order=STEP_ORDER,
                                     installer=installer_display)
        LOGGER.debug("Generate html page for %s", installer_display)
        with open("./display/" + version + "/functest/vims-" +
                  installer_display + ".html", "wb") as fh:
            fh.write(outputText)

LOGGER.info("vIMS report succesfully generated")
