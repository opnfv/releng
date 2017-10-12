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

from reporting.utils.scenarioResult import ScenarioResult
from reporting.utils import reporting_utils as utils
from scenarios import config as blacklist


# Logger
LOG = utils.getLogger("Yardstick-Status")


def get_scenario_data(version, installer):
    scenarios = utils.getScenarioStatus(installer, version)

    if 'colorado' == version:
        data = utils.getScenarioStatus(installer, 'stable/colorado')
        for archi, value in data.items():
            for k, v in value.items():
                if k not in scenarios[archi]:
                    scenarios[archi][k] = []
                scenarios[archi][k].extend(data[archi][k])

    for archi, value in scenarios.items():
        for scenario in value:
            if installer in blacklist and scenario in blacklist[installer]:
                scenarios[archi].pop(scenario)

    return scenarios


def write_history_data(version,
                       scenario,
                       installer,
                       archi,
                       ten_score,
                       percent):
    # Save daily results in a file
    history_file = './display/{}/yardstick/scenario_history.txt'.format(
        version)

    if not os.path.exists(history_file):
        with open(history_file, 'w') as f:
            f.write('date,scenario,installer,details,score\n')

    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    if installer == 'fuel':
        installer = '{}@{}'.format(installer, archi)
    with open(history_file, "a") as f:
        info = '{},{},{},{},{}\n'.format(date,
                                         scenario,
                                         installer,
                                         ten_score,
                                         percent)
        f.write(info)


def generate_page(scenario_data, installer, period, version, architecture):
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    templateLoader = jinja2.FileSystemLoader(".")
    template_env = jinja2.Environment(loader=templateLoader,
                                      autoescape=True)

    template_file = "./reporting/yardstick/template/index-status-tmpl.html"
    template = template_env.get_template(template_file)

    if installer == 'fuel':
        installer = '{}@{}'.format(installer, architecture)

    output_text = template.render(scenario_results=scenario_data,
                                  installer=installer,
                                  period=period,
                                  version=version,
                                  date=date)

    page_file = './display/{}/yardstick/status-{}.html'.format(version,
                                                               installer)
    with open(page_file, 'wb') as f:
        f.write(output_text)


def do_statistic(data):
    ten_score = 0
    for v in data:
        ten_score += v

    last_count = utils.get_config(
        'general.nb_iteration_tests_success_criteria')
    last_data = data[:last_count]
    last_score = 0
    for v in last_data:
        last_score += v

    percent = utils.get_percent(last_data, data)
    status = str(percent)
    last_score = '{}/{}'.format(last_score, len(last_data))
    ten_score = '{}/{}'.format(ten_score, len(data))

    if '100' == status:
        LOG.info(">>>>> scenario OK, save the information")
    else:
        LOG.info(">>>> scenario not OK, last 4 iterations = %s, \
                    last 10 days = %s" % (last_score, ten_score))

    return last_score, ten_score, percent, status


def generate_reporting_page(version, installer, archi, scenarios, period):
    scenario_data = {}

    # From each scenarios get results list
    for scenario, data in scenarios.items():
        LOG.info("---------------------------------")

        LOG.info("installer %s, version %s, scenario %s",
                 installer,
                 version,
                 scenario)
        last_score, ten_score, percent, status = do_statistic(data)
        write_history_data(version,
                           scenario,
                           installer,
                           archi,
                           ten_score,
                           percent)
        scenario_data[scenario] = ScenarioResult(status,
                                                 last_score,
                                                 ten_score,
                                                 percent)

        LOG.info("--------------------------")
    if scenario_data:
        generate_page(scenario_data, installer, period, version, archi)


def main():
    installers = utils.get_config('general.installers')
    versions = utils.get_config('general.versions')
    period = utils.get_config('general.period')

    LOG.info("*******************************************")
    LOG.info("*   Generating reporting scenario status  *")
    LOG.info("*   Data retention = %s days              *" % period)
    LOG.info("*                                         *")
    LOG.info("*******************************************")

    # For all the versions
    for version in versions:
        # For all the installers
        for installer in installers:
            # get scenarios results data
            scenarios = get_scenario_data(version, installer)
            for k, v in scenarios.items():
                generate_reporting_page(version, installer, k, v, period)


if __name__ == '__main__':
    main()
