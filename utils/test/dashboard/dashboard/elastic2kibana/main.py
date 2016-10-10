#! /usr/bin/env python
import json
import urlparse

import argparse

from common import elastic_access
from common import logger_utils
from conf import config
from conf import testcases
from dashboard_assembler import DashboardAssembler
from visualization_assembler import VisualizationsAssembler

logger = logger_utils.DashboardLogger('elastic2kibana').get

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config-file",
                    dest='config_file',
                    help="Config file location")

args = parser.parse_args()
CONF = config.APIConfig().parse(args.config_file)

_installers = {'fuel', 'apex', 'compass', 'joid'}


def _get_pods_and_scenarios(project_name, case_name, installer):
    query_json = json.JSONEncoder().encode({
        "query": {
            "bool": {
                "must": [
                    {"match_all": {}}
                ],
                "filter": [
                    {"match": {"installer": {"query": installer, "type": "phrase"}}},
                    {"match": {"project_name": {"query": project_name, "type": "phrase"}}},
                    {"match": {"case_name": {"query": case_name, "type": "phrase"}}}
                ]
            }
        }
    })

    elastic_data = elastic_access.get_docs(urlparse.urljoin(CONF.es_url, '/test_results/mongo2elastic'),
                                           CONF.es_creds,
                                           query_json)

    pods_and_scenarios = {}

    for data in elastic_data:
        pod = data['pod_name']
        if pod in pods_and_scenarios:
            pods_and_scenarios[pod].add(data['scenario'])
        else:
            pods_and_scenarios[pod] = {data['scenario']}

        if 'all' in pods_and_scenarios:
            pods_and_scenarios['all'].add(data['scenario'])
        else:
            pods_and_scenarios['all'] = {data['scenario']}

    return pods_and_scenarios


def construct_dashboards():
    """
    iterate over testcase and installer
    1. get available pods for each testcase/installer pair
    2. get available scenario for each testcase/installer/pod tuple
    3. construct KibanaInput and append

    :return: list of KibanaDashboards
    """
    dashboards = []
    for project, case_dicts in testcases.testcases_yaml.items():
        for case in case_dicts:
            case_name = case.get('name')
            vis_ps = case.get('visualizations')
            family = case.get('test_family')
            for installer in _installers:
                pods_and_scenarios = _get_pods_and_scenarios(project, case_name, installer)
                for vis_p in vis_ps:
                    for pod, scenarios in pods_and_scenarios.iteritems():
                        vissAssember = VisualizationsAssembler(project,
                                                              case_name,
                                                              installer,
                                                              pod,
                                                              scenarios,
                                                              vis_p,
                                                              CONF.es_url,
                                                              CONF.es_creds)
                        dashboardAssembler = DashboardAssembler(project,
                                                                case_name,
                                                                family,
                                                                installer,
                                                                pod,
                                                                vissAssember.visAssemblers,
                                                                CONF.es_url,
                                                                CONF.es_creds)
                        dashboards.append(dashboardAssembler)

    return dashboards


def generate_js_inputs(js_file_path, kibana_url, dashboards):
    js_dict = {}
    for dashboard in dashboards:
        dashboard_meta = dashboard.dashboard['metadata']
        test_family = dashboard_meta['test_family']
        test_label = dashboard_meta['label']

        if test_family not in js_dict:
            js_dict[test_family] = {}

        js_test_family = js_dict[test_family]

        if test_label not in js_test_family:
            js_test_family[test_label] = {}

        js_test_label = js_test_family[test_label]

        if dashboard.installer not in js_test_label:
            js_test_label[dashboard.installer] = {}

        js_installer = js_test_label[dashboard.installer]
        js_installer[dashboard.pod] = kibana_url + '#/dashboard/' + dashboard.id

    with open(js_file_path, 'w+') as js_file_fdesc:
        js_file_fdesc.write('var kibana_dashboard_links = ')
        js_file_fdesc.write(str(js_dict).replace("u'", "'"))


def main():
    dashboards = construct_dashboards()

    if CONF.is_js:
        generate_js_inputs(CONF.js_path, CONF.kibana_url, dashboards)
