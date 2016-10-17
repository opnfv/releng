import json

import utility
from dashboard.common import elastic_access


class VisStateBuilder(object):
    def __init__(self, vis_p):
        super(VisStateBuilder, self).__init__()
        self.vis_p = vis_p

    def build(self):
        name = self.vis_p.get('name')
        fields = self.vis_p.get('fields')

        aggs = []
        index = 1
        for field in fields:
            aggs.append({
                "id": index,
                "field": field.get("field")
            })
            index += 1

        template = utility.env.get_template('{}.json'.format(name))
        vis = template.render(aggs=aggs)
        return json.loads(vis)


class VisualizationAssembler(object):
    def __init__(self,
                 project,
                 case,
                 installer,
                 pod,
                 scenario,
                 vis_p,
                 es_url,
                 es_creds):
        super(VisualizationAssembler, self).__init__()
        self.project = project
        self.case = case
        self.installer = installer
        self.pod = pod
        self.scenario = scenario
        self.vis_p = vis_p
        self.es_url = es_url
        self.es_creds = es_creds
        self._assemble()
        self._publish()

    def _assemble(self):
        visState = VisStateBuilder(self.vis_p).build()
        self.vis_state_title = visState['title']

        vis = {
            "visState": json.dumps(visState),
            "filters": {
                "project_name": self.project,
                "case_name": self.case,
                "installer": self.installer,
                "metric": self.vis_state_title,
                "pod_name": self.pod,
                "scenario": self.scenario
            }
        }

        template = utility.env.get_template('visualization.json')

        self.visualization = json.loads(template.render(vis=vis))
        utility.dumps(self.visualization,
                      ['visState', 'description', 'uiStateJSON'])
        utility.dumps_2depth(self.visualization,
                             'kibanaSavedObjectMeta',
                             'searchSourceJSON')
        title = self.visualization['title']
        self.id = title.replace(' ', '-').replace('/', '-')

    def _publish(self):
        elastic_access.publish_kibana(self.es_url,
                                      self.es_creds,
                                      'visualization',
                                      self.id,
                                      self.visualization)
