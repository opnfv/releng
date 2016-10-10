import json

import utility
from common import elastic_access


class DashboardAssembler(object):
    def __init__(self,
                 project,
                 case,
                 family,
                 installer,
                 pod,
                 visualizations,
                 es_url,
                 es_creds):
        super(DashboardAssembler, self).__init__()
        self.project = project
        self.case = case
        self.test_family = family
        self.installer = installer
        self.pod = pod
        self.visualizations = visualizations
        self.es_url = es_url
        self.es_creds = es_creds
        self._assemble()
        self._publish()

    def _assemble(self):
        db = {
            "query": {
                "project_name": self.project,
                "case_name": self.case,
                "installer": self.installer,
                "metric": self.visualizations[0].vis_state_title,
                "pod": self.pod
            },
            "test_family": self.test_family,
            "ids": [visualization.id for visualization in self.visualizations]
        }
        template = utility.env.get_template('dashboard.json')
        self.dashboard = json.loads(template.render(db=db))
        utility.dumps(self.dashboard,
                      ['description',
                       'uiStateJSON',
                       'panelsJSON',
                       'optionsJSON'])
        utility.dumps_2depth(self.dashboard,
                             'kibanaSavedObjectMeta',
                             'searchSourceJSON')
        self.id = self.dashboard['title'].replace(' ', '-').replace('/', '-')
        return self

    def _publish(self):
        elastic_access.publish_kibana(self.es_url,
                                      self.es_creds,
                                      'dashboard',
                                      self.id,
                                      self.dashboard)
