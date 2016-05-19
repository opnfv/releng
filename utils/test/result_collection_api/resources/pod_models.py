__author__ = '__serena__'


class PodCreateRequest(object):
    def __init__(self, name='', mode='', details=''):
        self.name = name
        self.mode = mode
        self.details = details

    def format(self):
        return {
            "name": self.name,
            "mode": self.mode,
            "details": self.details,
        }


class Pod(PodCreateRequest):
    """ describes a POD platform """
    def __init__(self, name='', mode='', details='', _id='', create_date=''):
        super(Pod, self).__init__(name, mode, details)
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
        return p

    def format(self):
        f = super(Pod, self).format()
        f['creation_date'] = str(self.creation_date)
        return f

    def format_http(self):
        f = self.format()
        f['_id'] = str(self._id)
        return f


class Pods(object):
    def __init__(self, pods=list()):
        self.pods = pods

    @staticmethod
    def from_dict(res_dict):
        if res_dict is None:
            return None

        res = Pods()
        for pod in res_dict.get('pods'):
            res.pods.append(Pod.from_dict(pod))
        return res
