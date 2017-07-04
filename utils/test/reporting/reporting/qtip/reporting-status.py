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
import utils.reporting_utils as rp_utils
import utils.scenarioResult as sr

installers = rp_utils.get_config('general.installers')
versions = rp_utils.get_config('general.versions')
PERIOD = rp_utils.get_config('general.period')

# Logger
logger = rp_utils.getLogger("Qtip-Status")
reportingDate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

logger.info("*******************************************")
logger.info("*   Generating reporting scenario status  *")
logger.info("*   Data retention = {} days              *".format(PERIOD))
logger.info("*                                         *")
logger.info("*******************************************")


def prepare_profile_file(version):
    profile_dir = './display/{}/qtip'.format(version)
    if not os.path.exists(profile_dir):
        os.makedirs(profile_dir)

    profile_file = "{}/{}/scenario_history.txt".format(profile_dir,
                                                       version)
    if not os.path.exists(profile_file):
        with open(profile_file, 'w') as f:
            info = 'date,scenario,installer,details,score\n'
            f.write(info)
            f.close()
    return profile_file


def profile_results(results, installer, profile_fd):
    result_criterias = {}
    for s_p, s_p_result in results.iteritems():
        ten_criteria = len(s_p_result)
        ten_score = sum(s_p_result)

        LASTEST_TESTS = rp_utils.get_config(
            'general.nb_iteration_tests_success_criteria')
        four_result = s_p_result[:LASTEST_TESTS]
        four_criteria = len(four_result)
        four_score = sum(four_result)

        s_four_score = str(four_score / four_criteria)
        s_ten_score = str(ten_score / ten_criteria)

        info = '{},{},{},{},{}\n'.format(reportingDate,
                                         s_p,
                                         installer,
                                         s_ten_score,
                                         s_four_score)
        profile_fd.write(info)
        result_criterias[s_p] = sr.ScenarioResult('OK',
                                                  s_four_score,
                                                  s_ten_score,
                                                  '100')

        logger.info("--------------------------")
    return result_criterias


def render_html(prof_results, installer, version):
    template_loader = jinja2.FileSystemLoader(".")
    template_env = jinja2.Environment(loader=template_loader,
                                      autoescape=True)

    template_file = "./reporting/qtip/template/index-status-tmpl.html"
    template = template_env.get_template(template_file)

    render_outcome = template.render(prof_results=prof_results,
                                     installer=installer,
                                     period=PERIOD,
                                     version=version,
                                     date=reportingDate)

    with open('./display/{}/qtip/status-{}.html'.format(version, installer),
              'wb') as fh:
        fh.write(render_outcome)


def render_reporter():
    for version in versions:
        profile_file = prepare_profile_file(version)
        profile_fd = open(profile_file, 'a')
        for installer in installers:
            results = rp_utils.getQtipResults(version, installer)
            prof_results = profile_results(results, installer, profile_fd)
            render_html(prof_results=prof_results,
                        installer=installer,
                        version=version)
        profile_fd.close()
        logger.info("Manage export CSV")
        rp_utils.generate_csv(profile_file)
        logger.info("CSV generated...")


if __name__ == '__main__':
    render_reporter()
