#! /usr/bin/env python
import logging
import argparse
import shared_utils
import json
import urlparse

logger = logging.getLogger('create_kibana_dashboards')
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('/var/log/{}.log'.format('create_kibana_dashboards'))
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
logger.addHandler(file_handler)

_installers = {'fuel', 'apex', 'compass', 'joid'}

# see class VisualizationState for details on format
_testcases = [
    ('functest', 'tempest_smoke_serial',
     [
         {
             "metrics": [
                 {
                     "type": "avg",
                     "params": {
                         "field": "details.duration"
                     }
                 }
             ],
             "type": "line",
             "metadata": {
                 "label": "tempest_smoke_serial duration",
                 "test_family": "VIM"
             }
         },

         {
             "metrics": [
                 {
                     "type": "sum",
                     "params": {
                         "field": "details.tests"
                     }
                 },
                 {
                     "type": "sum",
                     "params": {
                         "field": "details.failures"
                     }
                 }
             ],
             "type": "histogram",
             "metadata": {
                 "label": "tempest_smoke_serial nr of tests/failures",
                 "test_family": "VIM"
             }
         },

         {
             "metrics": [
                 {
                     "type": "avg",
                     "params": {
                         "field": "details.success_percentage"
                     }
                 }
             ],
             "type": "line",
             "metadata": {
                 "label": "tempest_smoke_serial success percentage",
                 "test_family": "VIM"
             }
         }
     ]
     ),

    ('functest', 'rally_sanity',
     [
         {
             "metrics": [
                 {
                     "type": "avg",
                     "params": {
                         "field": "details.duration"
                     }
                 }
             ],
             "type": "line",
             "metadata": {
                 "label": "rally_sanity duration",
                 "test_family": "VIM"
             }
         },

         {
             "metrics": [
                 {
                     "type": "avg",
                     "params": {
                         "field": "details.tests"
                     }
                 }
             ],
             "type": "histogram",
             "metadata": {
                 "label": "rally_sanity nr of tests",
                 "test_family": "VIM"
             }
         },

         {
             "metrics": [
                 {
                     "type": "avg",
                     "params": {
                         "field": "details.success_percentage"
                     }
                 }
             ],
             "type": "line",
             "metadata": {
                 "label": "rally_sanity success percentage",
                 "test_family": "VIM"
             }
         }
     ]
     ),

    ('functest', 'vping_ssh',
     [
         {
             "metrics": [
                 {
                     "type": "avg",
                     "params": {
                         "field": "details.duration"
                     }
                 }
             ],
             "type": "line",
             "metadata": {
                 "label": "vPing duration",
                 "test_family": "VIM"
             }
         }
     ]
     ),

    ('functest', 'vping_userdata',
     [
         {
             "metrics": [
                 {
                     "type": "avg",
                     "params": {
                         "field": "details.duration"
                     }
                 }
             ],
             "type": "line",
             "metadata": {
                 "label": "vPing_userdata duration",
                 "test_family": "VIM"
             }
         }
     ]
     ),

    ('functest', 'odl',
     [
         {
             "metrics": [
                 {
                     "type": "sum",
                     "params": {
                         "field": "details.tests"
                     }
                 },
                 {
                     "type": "sum",
                     "params": {
                         "field": "details.failures"
                     }
                 }
             ],
             "type": "histogram",
             "metadata": {
                 "label": "ODL nr of tests/failures",
                 "test_family": "Controller"
             }
         },

         {
             "metrics": [
                 {
                     "type": "avg",
                     "params": {
                         "field": "details.success_percentage"
                     }
                 }
             ],
             "type": "line",
             "metadata": {
                 "label": "ODL success percentage",
                 "test_family": "Controller"
             }
         }
     ]
     ),

    ('functest', 'onos',
     [
         {
             "metrics": [
                 {
                     "type": "avg",
                     "params": {
                         "field": "details.FUNCvirNet.duration"
                     }
                 }
             ],
             "type": "line",
             "metadata": {
                 "label": "ONOS FUNCvirNet duration",
                 "test_family": "Controller"
             }
         },

         {
             "metrics": [
                 {
                     "type": "sum",
                     "params": {
                         "field": "details.FUNCvirNet.tests"
                     }
                 },
                 {
                     "type": "sum",
                     "params": {
                         "field": "details.FUNCvirNet.failures"
                     }
                 }
             ],
             "type": "histogram",
             "metadata": {
                 "label": "ONOS FUNCvirNet nr of tests/failures",
                 "test_family": "Controller"
             }
         },

         {
             "metrics": [
                 {
                     "type": "avg",
                     "params": {
                         "field": "details.FUNCvirNetL3.duration"
                     }
                 }
             ],
             "type": "line",
             "metadata": {
                 "label": "ONOS FUNCvirNetL3 duration",
                 "test_family": "Controller"
             }
         },

         {
             "metrics": [
                 {
                     "type": "sum",
                     "params": {
                         "field": "details.FUNCvirNetL3.tests"
                     }
                 },
                 {
                     "type": "sum",
                     "params": {
                         "field": "details.FUNCvirNetL3.failures"
                     }
                 }
             ],
             "type": "histogram",
             "metadata": {
                 "label": "ONOS FUNCvirNetL3 nr of tests/failures",
                 "test_family": "Controller"
             }
         }
     ]
     ),

    ('functest', 'vims',
     [
         {
             "metrics": [
                 {
                     "type": "sum",
                     "params": {
                         "field": "details.sig_test.tests"
                     }
                 },
                 {
                     "type": "sum",
                     "params": {
                         "field": "details.sig_test.failures"
                     }
                 },
                 {
                     "type": "sum",
                     "params": {
                         "field": "details.sig_test.passed"
                     }
                 },
                 {
                     "type": "sum",
                     "params": {
                         "field": "details.sig_test.skipped"
                     }
                 }
             ],
             "type": "histogram",
             "metadata": {
                 "label": "vIMS nr of tests/failures/passed/skipped",
                 "test_family": "Features"
             }
         },

         {
             "metrics": [
                 {
                     "type": "avg",
                     "params": {
                         "field": "details.vIMS.duration"
                     }
                 },
                 {
                     "type": "avg",
                     "params": {
                         "field": "details.orchestrator.duration"
                     }
                 },
                 {
                     "type": "avg",
                     "params": {
                         "field": "details.sig_test.duration"
                     }
                 }
             ],
             "type": "histogram",
             "metadata": {
                 "label": "vIMS/ochestrator/test duration",
                 "test_family": "Features"
             }
         }
     ]
     ),

    ('promise', 'promise',
     [
         {
             "metrics": [
                 {
                     "type": "avg",
                     "params": {
                         "field": "details.duration"
                     }
                 }
             ],
             "type": "line",
             "metadata": {
                 "label": "promise duration",
                 "test_family": "Features"
             }
         },

         {
             "metrics": [
                 {
                     "type": "sum",
                     "params": {
                         "field": "details.tests"
                     }
                 },
                 {
                     "type": "sum",
                     "params": {
                         "field": "details.failures"
                     }
                 }
             ],
             "type": "histogram",
             "metadata": {
                 "label": "promise nr of tests/failures",
                 "test_family": "Features"
             }
         }
     ]
     ),

    ('doctor', 'doctor-notification',
     [
         {
             "metrics": [
                 {
                     "type": "avg",
                     "params": {
                         "field": "details.duration"
                     }
                 }
             ],
             "type": "line",
             "metadata": {
                 "label": "doctor-notification duration",
                 "test_family": "Features"
             }
         }
     ]
     )
]


class KibanaDashboard(dict):
    def __init__(self, project_name, case_name, installer, pod, scenarios, visualization_detail):
        super(KibanaDashboard, self).__init__()
        self.project_name = project_name
        self.case_name = case_name
        self.installer = installer
        self.pod = pod
        self.scenarios = scenarios
        self.visualization_detail = visualization_detail
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
                                                                   self.visualization_detail))

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
        self['metadata'] = self.visualization_detail['metadata']

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
    def __init__(self, input_dict):
        """
        dict structure:
            {
            "metrics":
                [
                    {
                        "type": type,           # default sum
                        "params": {
                            "field": field      # mandatory, no default
                    },
                    {metric2}
                ],
            "segments":
                [
                    {
                        "type": type,           # default date_histogram
                        "params": {
                            "field": field      # default start_date
                    },
                    {segment2}
                ],
            "type": type,                       # default area
            "mode": mode,                       # default grouped for type 'histogram', stacked for other types
            "metadata": {
                    "label": "tempest_smoke_serial duration",# mandatory, no default
                    "test_family": "VIM"        # mandatory, no default
                }
            }

        default modes:
            type histogram: grouped
            type area: stacked

        :param input_dict:
        :return:
        """
        super(VisualizationState, self).__init__()
        metrics = input_dict['metrics']
        segments = [] if 'segments' not in input_dict else input_dict['segments']

        graph_type = 'area' if 'type' not in input_dict else input_dict['type']
        self['type'] = graph_type

        if 'mode' not in input_dict:
            if graph_type == 'histogram':
                mode = 'grouped'
            else:
                # default
                mode = 'stacked'
        else:
            mode = input_dict['mode']
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
        for metric in metrics:
            self['aggs'].append({
                "id": str(i),
                "type": 'sum' if 'type' not in metric else metric['type'],
                "schema": "metric",
                "params": {
                    "field": metric['params']['field']
                }
            })
            i += 1

        if len(segments) > 0:
            for segment in segments:
                self['aggs'].append({
                    "id": str(i),
                    "type": 'date_histogram' if 'type' not in segment else segment['type'],
                    "schema": "metric",
                    "params": {
                        "field": "start_date" if ('params' not in segment or 'field' not in segment['params'])
                        else segment['params']['field'],
                        "interval": "auto",
                        "customInterval": "2h",
                        "min_doc_count": 1,
                        "extended_bounds": {}
                    }
                })
                i += 1
        else:
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
    def __init__(self, project_name, case_name, installer, pod, scenario, detail):
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
        vis_state = VisualizationState(detail)
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
    for project_name, case_name, visualization_details in _testcases:
        for installer in _installers:
            pods_and_scenarios = _get_pods_and_scenarios(project_name, case_name, installer)
            for visualization_detail in visualization_details:
                for pod, scenarios in pods_and_scenarios.iteritems():
                    kibana_dashboards.append(KibanaDashboard(project_name, case_name, installer, pod, scenarios,
                                                             visualization_detail))
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

