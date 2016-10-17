#! /usr/bin/env python
import json
import urlparse

import argparse

from dashboard.common import elastic_access
from dashboard.common import logger_utils
from dashboard.conf import config
from dashboard.conf import testcases
from dashboard_assembler import DashboardAssembler
from visualization_assembler import VisualizationAssembler

logger = logger_utils.DashboardLogger('elastic2kibana').get

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config-file",
                    dest='config_file',
                    help="Config file location")

args = parser.parse_args()
CONF = config.APIConfig().parse(args.config_file)

_installers = {'fuel', 'apex', 'compass', 'joid'}


class KibanaConstructor(object):
    def __init__(self):
        super(KibanaConstructor, self).__init__()
        self.js_dict = {}

    def construct(self):
        for project, case_dicts in testcases.testcases_yaml.items():
            for case in case_dicts:
                self._construct_by_case(project, case)
        return self

    def _construct_by_case(self, project, case):
        case_name = case.get('name')
        vis_ps = case.get('visualizations')
        family = case.get('test_family')
        for vis_p in vis_ps:
            self._construct_by_vis(project, case_name, family, vis_p)

    def _construct_by_vis(self, project, case, family, vis_p):
        for installer in _installers:
            pods_and_scenarios = self._get_pods_and_scenarios(project,
                                                              case,
                                                              installer)
            for pod, scenarios in pods_and_scenarios.iteritems():
                visualizations = self._construct_visualizations(project,
                                                                case,
                                                                installer,
                                                                pod,
                                                                scenarios,
                                                                vis_p,
                                                                CONF.es_url,
                                                                CONF.es_creds)
                dashboard = DashboardAssembler(project,
                                               case,
                                               family,
                                               installer,
                                               pod,
                                               visualizations,
                                               CONF.es_url,
                                               CONF.es_creds)
                self._set_js_dict(case,
                                  pod,
                                  installer,
                                  family,
                                  vis_p.get('name'),
                                  dashboard.id)

    @staticmethod
    def _construct_visualizations(project,
                                  case,
                                  installer,
                                  pod,
                                  scenarios,
                                  vis_p,
                                  es_url,
                                  es_creds):
        visualizations = []
        for scenario in scenarios:
            visualizations.append(VisualizationAssembler(project,
                                                         case,
                                                         installer,
                                                         pod,
                                                         scenario,
                                                         vis_p,
                                                         es_url,
                                                         es_creds))
        return visualizations

    def _set_js_dict(self, case, pod, installer, family, metric, id):
        test_label = '{} {}'.format(case, metric)
        if family not in self.js_dict:
            self.js_dict[family] = {}

        js_test_family = self.js_dict[family]

        if test_label not in js_test_family:
            js_test_family[test_label] = {}

        js_test_label = js_test_family[test_label]

        if installer not in js_test_label:
            js_test_label[installer] = {}

        js_installer = js_test_label[installer]
        js_installer[pod] = CONF.kibana_url + '#/dashboard/' + id

    def config_js(self):
        with open(CONF.js_path, 'w+') as conf_js_fdesc:
            conf_js_fdesc.write('var kibana_dashboard_links = ')
            conf_js_fdesc.write(str(self.js_dict).replace("u'", "'"))

    def _get_pods_and_scenarios(self, project, case, installer):
        query = json.JSONEncoder().encode({
            "query": {
                "bool": {
                    "must": [
                        {"match_all": {}}
                    ],
                    "filter": [
                        {"match": {"installer": installer}},
                        {"match": {"project_name": project}},
                        {"match": {"case_name": case}}
                    ]
                }
            }
        })

        elastic_data = elastic_access.get_docs(
            urlparse.urljoin(CONF.es_url, '/testapi/results'),
            CONF.es_creds,
            query)

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


def main():
    KibanaConstructor().construct().config_js()
