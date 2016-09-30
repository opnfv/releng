#! /usr/bin/env python
import json
import urlparse

import argparse
from jinja2 import PackageLoader, Environment

from common import elastic_access
from common import logger_utils
from conf import testcases
from conf.config import APIConfig

logger = logger_utils.DashboardLogger('elastic2kibana').get

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config-file",
                    dest='config_file',
                    help="Config file location")

args = parser.parse_args()
CONF = APIConfig().parse(args.config_file)
base_elastic_url = CONF.elastic_url
generate_inputs = CONF.is_js
input_file_path = CONF.js_path
kibana_url = CONF.kibana_url
es_creds = CONF.elastic_creds

_installers = {'fuel', 'apex', 'compass', 'joid'}

env = Environment(loader=PackageLoader('elastic2kibana', 'templates'))
env.filters['jsonify'] = json.dumps


def dumps(self, items):
    for key in items:
        self.visualization[key] = json.dumps(self.visualization[key])


def dumps_2depth(self, key1, key2):
    self.visualization[key1][key2] = json.dumps(self.visualization[key1][key2])


class Dashboard(dict):
    def __init__(self, project_name, case_name, family, installer, pod, scenarios, visualization):
        super(Dashboard, self).__init__()
        self.project_name = project_name
        self.case_name = case_name
        self.family = family
        self.installer = installer
        self.pod = pod
        self.scenarios = scenarios
        self.visualization = visualization
        self._visualization_title = None
        self._kibana_visualizations = []
        self._kibana_dashboard = None
        self._create_visualizations()
        self._create()

    def _create_visualizations(self):
        for scenario in self.scenarios:
            self._kibana_visualizations.append(Visualization(self.project_name,
                                                             self.case_name,
                                                             self.installer,
                                                             self.pod,
                                                             scenario,
                                                             self.visualization))

        self._visualization_title = self._kibana_visualizations[0].vis_state_title

    def _publish_visualizations(self):
        for visualization in self._kibana_visualizations:
            url = urlparse.urljoin(base_elastic_url, '/.kibana/visualization/{}'.format(visualization.id))
            logger.debug("publishing visualization '{}'".format(url))
            # logger.error("_publish_visualization: %s" % visualization)
            elastic_access.publish_docs(url, es_creds, visualization)

    def _create(self):
        db = {
            "query": {
                "project_name": self.project_name,
                "case_name": self.case_name,
                "installer": self.installer,
                "metric": self._visualization_title,
                "pod": self.pod
            },
            "test_family": self.family,
            "ids": [visualization.id for visualization in self._kibana_visualizations]
        }
        template = env.get_template('dashboard.json')
        self.dashboard = json.loads(template.render(db=db))
        dumps(self.dashboard, ['description', 'uiStateJSON', 'panelsJSON','optionsJSON'])
        dumps_2depth(self.dashboard, 'kibanaSavedObjectMeta', 'searchSourceJSON')
        self.id = self.dashboard['title'].replace(' ', '-').replace('/', '-')


    def _publish(self):
        url = urlparse.urljoin(base_elastic_url, '/.kibana/dashboard/{}'.format(self.id))
        logger.debug("publishing dashboard '{}'".format(url))
        #logger.error("dashboard: %s" % json.dumps(self.dashboard))
        elastic_access.publish_docs(url, es_creds, self.dashboard)

    def publish(self):
        self._publish_visualizations()
        self._publish()


class VisStateBuilder(object):
    def __init__(self, visualization):
        super(VisStateBuilder, self).__init__()
        self.visualization = visualization

    def build(self):
        name = self.visualization.get('name')
        fields = self.visualization.get('fields')

        aggs = []
        index = 1
        for field in fields:
            aggs.append({
                "id": index,
                "field": field.get("field")
            })
            index += 1

        template = env.get_template('{}.json'.format(name))
        vis = template.render(aggs=aggs)
        return json.loads(vis)


class Visualization(object):
    def __init__(self, project_name, case_name, installer, pod, scenario, visualization):
        """
        We need two things
        1. filter created from
            project_name
            case_name
            installer
            pod
            scenario
        2. visualization state
            field for y axis (metric) with type (avg, sum, etc.)
            field for x axis (segment) with type (date_histogram)

        :return:
        """
        super(Visualization, self).__init__()
        visState = VisStateBuilder(visualization).build()
        self.vis_state_title = visState['title']

        vis = {
            "visState": json.dumps(visState),
            "filters": {
                "project_name": project_name,
                "case_name": case_name,
                "installer": installer,
                "metric": self.vis_state_title,
                "pod_name": pod,
                "scenario": scenario
            }
        }

        template = env.get_template('visualization.json')

        self.visualization = json.loads(template.render(vis=vis))
        dumps(self.visualization, ['visState', 'description', 'uiStateJSON'])
        dumps_2depth(self.visualization, 'kibanaSavedObjectMeta', 'searchSourceJSON')
        self.id = self.visualization['title'].replace(' ', '-').replace('/', '-')


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

    elastic_data = elastic_access.get_docs(urlparse.urljoin(base_elastic_url, '/test_results/mongo2elastic'),
                                           es_creds,
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
    kibana_dashboards = []
    for project, case_dicts in testcases.testcases_yaml.items():
        for case in case_dicts:
            case_name = case.get('name')
            visualizations = case.get('visualizations')
            family = case.get('test_family')
            for installer in _installers:
                pods_and_scenarios = _get_pods_and_scenarios(project, case_name, installer)
                for visualization in visualizations:
                    for pod, scenarios in pods_and_scenarios.iteritems():
                        kibana_dashboards.append(Dashboard(project,
                                                           case_name,
                                                           family,
                                                           installer,
                                                           pod,
                                                           scenarios,
                                                           visualization))
    return kibana_dashboards


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

    for kibana_dashboard in dashboards:
        kibana_dashboard.publish()

    if generate_inputs:
        generate_js_inputs(input_file_path, kibana_url, dashboards)
