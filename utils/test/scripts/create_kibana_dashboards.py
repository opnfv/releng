#! /usr/bin/env python
import json
import urlparse

import argparse

import conf_utils
import logger_utils
import shared_utils

logger = logger_utils.KibanaDashboardLogger('elastic2kibana').get

_installers = {'fuel', 'apex', 'compass', 'joid'}


class KibanaDashboard(dict):
    def __init__(self, project_name, case_name, family, installer, pod, scenarios, visualization):
        super(KibanaDashboard, self).__init__()
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
            self._kibana_visualizations.append(KibanaVisualization(self.project_name,
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
            shared_utils.publish_json(visualization, es_creds, url)

    def _construct_panels(self):
        size_x = 6
        size_y = 3
        max_columns = 7
        column = 1
        row = 1
        panel_index = 1
        panels_json = []
        for visualization in self._kibana_visualizations:
            panels_json.append({
                "id": visualization.id,
                "type": 'visualization',
                "panelIndex": panel_index,
                "size_x": size_x,
                "size_y": size_y,
                "col": column,
                "row": row
            })
            panel_index += 1
            column += size_x
            if column > max_columns:
                column = 1
                row += size_y
        return json.dumps(panels_json, separators=(',', ':'))

    def _create(self):
        self['title'] = '{} {} {} {} {}'.format(self.project_name,
                                                self.case_name,
                                                self.installer,
                                                self._visualization_title,
                                                self.pod)
        self.id = self['title'].replace(' ', '-').replace('/', '-')

        self['hits'] = 0
        self['description'] = "Kibana dashboard for project_name '{}', case_name '{}', installer '{}', data '{}' and" \
                              " pod '{}'".format(self.project_name,
                                                 self.case_name,
                                                 self.installer,
                                                 self._visualization_title,
                                                 self.pod)
        self['panelsJSON'] = self._construct_panels()
        self['optionsJSON'] = json.dumps({
            "darkTheme": False
        },
            separators=(',', ':'))
        self['uiStateJSON'] = "{}"
        self['scenario'] = 1
        self['timeRestore'] = False
        self['kibanaSavedObjectMeta'] = {
            'searchSourceJSON': json.dumps({
                "filter": [
                    {
                        "query": {
                            "query_string": {
                                "query": "*",
                                "analyze_wildcard": True
                            }
                        }
                    }
                ]
            },
                separators=(',', ':'))
        }

        label = self.case_name
        if 'label' in self.visualization:
            label += " %s" % self.visualization.get('label')
        label += " %s" % self.visualization.get('name')
        self['metadata'] = {
            "label": label,
            "test_family": self.family
        }

    def _publish(self):
        url = urlparse.urljoin(base_elastic_url, '/.kibana/dashboard/{}'.format(self.id))
        logger.debug("publishing dashboard '{}'".format(url))
        shared_utils.publish_json(self, es_creds, url)

    def publish(self):
        self._publish_visualizations()
        self._publish()


class KibanaSearchSourceJSON(dict):
    """
    "filter": [
                    {"match": {"installer": {"query": installer, "type": "phrase"}}},
                    {"match": {"project_name": {"query": project_name, "type": "phrase"}}},
                    {"match": {"case_name": {"query": case_name, "type": "phrase"}}}
                ]
    """

    def __init__(self, project_name, case_name, installer, pod, scenario):
        super(KibanaSearchSourceJSON, self).__init__()
        self["filter"] = [
            {"match": {"project_name": {"query": project_name, "type": "phrase"}}},
            {"match": {"case_name": {"query": case_name, "type": "phrase"}}},
            {"match": {"installer": {"query": installer, "type": "phrase"}}},
            {"match": {"scenario": {"query": scenario, "type": "phrase"}}}
        ]
        if pod != 'all':
            self["filter"].append({"match": {"pod_name": {"query": pod, "type": "phrase"}}})


class VisualizationState(dict):
    def __init__(self, visualization):
        super(VisualizationState, self).__init__()
        name = visualization.get('name')
        fields = visualization.get('fields')

        if name == 'tests_failures':
            mode = 'grouped'
            metric_type = 'sum'
            self['type'] = 'histogram'
        else:
            # duration or success_percentage
            mode = 'stacked'
            metric_type = 'avg'
            self['type'] = 'line'

        self['params'] = {
            "shareYAxis": True,
            "addTooltip": True,
            "addLegend": True,
            "smoothLines": False,
            "scale": "linear",
            "interpolate": "linear",
            "mode": mode,
            "times": [],
            "addTimeMarker": False,
            "defaultYExtents": False,
            "setYExtents": False,
            "yAxis": {}
        }

        self['aggs'] = []

        i = 1
        for field in fields:
            self['aggs'].append({
                "id": str(i),
                "type": metric_type,
                "schema": "metric",
                "params": {
                    "field": field.get('field')
                }
            })
            i += 1

        self['aggs'].append({
                "id": str(i),
                "type": 'date_histogram',
                "schema": "segment",
                "params": {
                    "field": "start_date",
                    "interval": "auto",
                    "customInterval": "2h",
                    "min_doc_count": 1,
                    "extended_bounds": {}
                }
            })

        self['listeners'] = {}
        self['title'] = ' '.join(['{} {}'.format(x['type'], x['params']['field']) for x in self['aggs']
                                  if x['schema'] == 'metric'])


class KibanaVisualization(dict):
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
        super(KibanaVisualization, self).__init__()
        vis_state = VisualizationState(visualization)
        self.vis_state_title = vis_state['title']
        self['title'] = '{} {} {} {} {} {}'.format(project_name,
                                                   case_name,
                                                   self.vis_state_title,
                                                   installer,
                                                   pod,
                                                   scenario)
        self.id = self['title'].replace(' ', '-').replace('/', '-')
        self['visState'] = json.dumps(vis_state, separators=(',', ':'))
        self['uiStateJSON'] = "{}"
        self['description'] = "Kibana visualization for project_name '{}', case_name '{}', data '{}', installer '{}'," \
                              " pod '{}' and scenario '{}'".format(project_name,
                                                                  case_name,
                                                                  self.vis_state_title,
                                                                  installer,
                                                                  pod,
                                                                  scenario)
        self['scenario'] = 1
        self['kibanaSavedObjectMeta'] = {"searchSourceJSON": json.dumps(KibanaSearchSourceJSON(project_name,
                                                                                               case_name,
                                                                                               installer,
                                                                                               pod,
                                                                                               scenario),
                                                                        separators=(',', ':'))}


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

    elastic_data = shared_utils.get_elastic_data(urlparse.urljoin(base_elastic_url, '/test_results/mongo2elastic'),
                                                 es_creds, query_json)

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
    for project, case_dicts in conf_utils.testcases_yaml.items():
        for case in case_dicts:
            case_name = case.get('name')
            visualizations = case.get('visualizations')
            family = case.get('test_family')
            for installer in _installers:
                pods_and_scenarios = _get_pods_and_scenarios(project, case_name, installer)
                for visualization in visualizations:
                    for pod, scenarios in pods_and_scenarios.iteritems():
                        kibana_dashboards.append(KibanaDashboard(project,
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
        dashboard_meta = dashboard['metadata']
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create Kibana dashboards from data in elasticsearch')
    parser.add_argument('-e', '--elasticsearch-url', default='http://localhost:9200',
                        help='the url of elasticsearch, defaults to http://localhost:9200')

    parser.add_argument('-js', '--generate_js_inputs', action='store_true',
                        help='Use this argument to generate javascript inputs for kibana landing page')

    parser.add_argument('--js_path', default='/usr/share/nginx/html/kibana_dashboards/conf.js',
                        help='Path of javascript file with inputs for kibana landing page')

    parser.add_argument('-k', '--kibana_url', default='https://testresults.opnfv.org/kibana/app/kibana',
                        help='The url of kibana for javascript inputs')

    parser.add_argument('-u', '--elasticsearch-username', default=None,
                        help='The username with password for elasticsearch in format username:password')

    args = parser.parse_args()
    base_elastic_url = args.elasticsearch_url
    generate_inputs = args.generate_js_inputs
    input_file_path = args.js_path
    kibana_url = args.kibana_url
    es_creds = args.elasticsearch_username

    dashboards = construct_dashboards()

    for kibana_dashboard in dashboards:
        kibana_dashboard.publish()

    if generate_inputs:
        generate_js_inputs(input_file_path, kibana_url, dashboards)
