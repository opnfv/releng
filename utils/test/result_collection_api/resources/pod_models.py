from models import MetaCreateResponse, MetaGetResponse


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

    @staticmethod
    def from_dict(req_dict):
        if req_dict is None:
            return None

        req = PodCreateRequest()
        req.name = req_dict.get('name')
        req.mode = req_dict.get('mode')
        req.details = req_dict.get('details')
        return req


class Pod(PodCreateRequest):
    """ describes a POD platform """
    def __init__(self, name='', mode='', details='', _id='', create_date=''):
        super(Pod, self).__init__(name, mode, details)
        self._id = _id
        self.creation_date = create_date

    @staticmethod
    def pod_from_dict(pod_dict):
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


class PodCreateResponse(object):
    def __init__(self, pod=None, meta=None):
        self.pod = pod
        self.meta = meta

    @staticmethod
    def from_dict(res_dict):
        if res_dict is None:
            return None

        res = PodCreateResponse()
        res.pod = Pod.pod_from_dict(res_dict.get('pod'))
        res.meta = MetaCreateResponse.from_dict(res_dict.get('meta'))
        return res


class PodGetResponse(PodCreateRequest):
    def __init__(self, name='', mode='', details='', create_date=''):
        self.creation_date = create_date
        super(PodGetResponse, self).__init__(name, mode, details)

    @staticmethod
    def from_dict(req_dict):
        if req_dict is None:
            return None

        res = PodGetResponse()
        res.creation_date = str(req_dict.get('creation_date'))
        res.name = req_dict.get('name')
        res.mode = req_dict.get('mode')
        res.details = req_dict.get('details')
        return res


class PodsGetResponse(object):
    def __init__(self, pods=[], meta=None):
        self.pods = pods
        self.meta = meta

    @staticmethod
    def from_dict(res_dict):
        if res_dict is None:
            return None

        res = PodsGetResponse()
        for pod in res_dict.get('pods'):
            res.pods.append(PodGetResponse.from_dict(pod))
        res.meta = MetaGetResponse.from_dict(res_dict.get('meta'))
        return res
