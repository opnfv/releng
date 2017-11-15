#!/usr/bin/python
#
# This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
import os
import datetime
import logging
from itertools import ifilter

import jinja2

from reporting.utils import reporting_utils
from reporting.utils.scenarioResult import ScenarioResult

LOG = reporting_utils.getLogger("Vsperf-Status")
LOG.setLevel(logging.DEBUG)

HISTORY_FILE = "./display/{}/vsperf/scenario_history.txt"
TEMPLATE_FILE = "./reporting/vsperf/template/index-status-tmpl.html"
TARGET_FILE = "./display/{}/vsperf/reporting.html"


def _get_version_data(data):
    version_data = {}
    for ele in data:
        try:
            version = ele['build_tag'].split('-')[-2]
        except (KeyError, TypeError, IndexError):
            continue

        if version not in version_data:
            version_data[version] = []
        version_data[version].append(ele)
    return version_data


def _get_case_data(data):
    case_data = {}
    for ele in data:
        case_name = ele['case_name']
        if case_name not in case_data:
            case_data[case_name] = []
        case_data[case_name].append(ele)
    return case_data


def _get_score(data):
    count = len(list(ifilter(lambda r: r['criteria'] == 'PASS', data)))
    total = len(data)
    return count, total


def _get_result_obj(version, case, data):
    fifty_pass, fifty_total = _get_score(data)
    four_pass, four_total = _get_score(data[:4])
    status = (four_pass * 100) / four_total
    four_score = '{}/{}'.format(four_pass, four_total)
    fifty_score = '{}/{}'.format(fifty_pass, fifty_total)
    percent = str(status)
    url = reporting_utils.getJenkinsUrl(data[-1]['build_tag'])
    LOG.debug('Last four score: %s', four_score)
    LOG.debug('Fifty days score: %s', fifty_score)
    LOG.debug('Last Four percent: %s', percent)

    _write_history_file(version, case, fifty_score, percent)

    return ScenarioResult(status, four_score, fifty_score, percent, url)


def _write_history_file(version, case, fifty_score, percent):
    file_path = HISTORY_FILE.format(version)

    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            info = 'date,case,details,score\n'
            f.write(info)

    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    with open(file_path, "a") as f:
        info = '{},{},{},{}\n'.format(date, case, fifty_score, percent)
        f.write(info)


def _do_generate(version, case_result):
    templateLoader = jinja2.FileSystemLoader(".")
    templateEnv = jinja2.Environment(loader=templateLoader,
                                     autoescape=True)

    template = templateEnv.get_template(TEMPLATE_FILE)

    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    outputText = template.render(case_result=case_result,
                                 period=50,
                                 version=version,
                                 date=date)

    with open(TARGET_FILE.format(version), 'wb') as f:
        f.write(outputText)


def _generate_reporting(version, data):
    case_result = {}
    case_data = _get_case_data(data)
    for case, value in case_data.items():
        LOG.debug('version: %s, case: %s', version, case)
        case_result[case] = _get_result_obj(version, case, value)
    _do_generate(version, case_result)


def main():
    LOG.info("*******************************************")
    LOG.info("*    Generating vsperf reporting status   *")
    LOG.info("*    Data retention = 50 days             *")
    LOG.info("*                                         *")
    LOG.info("*******************************************")

    data = reporting_utils.getScenarios("vsperf",
                                        None,
                                        "fuel",
                                        None,
                                        period=50)
    version_data = _get_version_data(data['vsperf'])

    for version in {'master', 'danube', 'euphrates'}:
        _generate_reporting(version, version_data.get(version, []))

    LOG.info("End")


if __name__ == '__main__':
    main()
