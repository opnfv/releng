from opnfv_testapi.tornado_swagger_ui.tornado_swagger import swagger

__author__ = '__serena__'

# name: name of the POD e.g. zte-1
# mode: metal or virtual
# details: any detail
# role: ci-pod or community-pod or single-node


@swagger.model()
class PodCreateRequest(object):
    def __init__(self, name, mode='', details='', role=""):
        self.name = name
        self.mode = mode
        self.details = details
        self.role = role

    def format(self):
        return {
            "name": self.name,
            "mode": self.mode,
            "details": self.details,
            "role": self.role,
        }


@swagger.model()
class Pod(PodCreateRequest):
    def __init__(self,
                 name='', mode='', details='',
                 role="", _id='', create_date=''):
        super(Pod, self).__init__(name, mode, details, role)
        self._id = _id
        self.creation_date = create_date

    @staticmethod
    def from_dict(pod_dict):
        if pod_dict is None:
            return None

        p = Pod()
        p._id = pod_dict.get('_id')
        p.creation_date = str(pod_dict.get('creation_date'))
        p.name = pod_dict.get('name')
        p.mode = pod_dict.get('mode')
        p.details = pod_dict.get('details')
        p.role = pod_dict.get('role')
        return p

    def format(self):
        f = super(Pod, self).format()
        f['creation_date'] = str(self.creation_date)
        return f

    def format_http(self):
        f = self.format()
        f['_id'] = str(self._id)
        return f


@swagger.model()
class Pods(object):
    """
        @property pods:
        @ptype pods: C{list} of L{Pod}
    """
    def __init__(self):
        self.pods = list()

    @staticmethod
    def from_dict(res_dict):
        if res_dict is None:
            return None

        res = Pods()
        for pod in res_dict.get('pods'):
            res.pods.append(Pod.from_dict(pod))
        return res
