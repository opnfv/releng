class Details(object):
    def __init__(self, timestart=None, duration=None, status=None):
        self.timestart = timestart
        self.duration = duration
        self.status = status

    def format(self):
        return {
            "timestart": self.timestart,
            "duration": self.duration,
            "status": self.status
        }

    @staticmethod
    def from_dict(a_dict):

        if a_dict is None:
            return None

        t = Details()
        t.timestart = a_dict.get('timestart')
        t.duration = a_dict.get('duration')
        t.status = a_dict.get('status')
        return t


class ResultCreateRequest(object):
    def __init__(self,
                 pod_name=None,
                 project_name=None,
                 case_name=None,
                 installer=None,
                 version=None,
                 description=None,
                 details=None,
                 build_tag=None,
                 scenario=None,
                 criteria=None,
                 trust_indicator=None):
        self.pod_name = pod_name
        self.project_name = project_name
        self.case_name = case_name
        self.installer = installer
        self.version = version
        self.description = description
        self.details = details
        self.build_tag = build_tag
        self.scenario = scenario
        self.criteria = criteria
        self.trust_indicator = trust_indicator

    def format(self):
        return {
            "pod_name": self.pod_name,
            "project_name": self.project_name,
            "case_name": self.case_name,
            "installer": self.installer,
            "version": self.version,
            "description": self.description,
            "details": self.details.format(),
            "build_tag": self.build_tag,
            "scenario": self.scenario,
            "criteria": self.criteria,
            "trust_indicator": self.trust_indicator
        }


class TestResult:
    """ Describes a test result"""

    def __init__(self):
        self._id = None
        self.case_name = None
        self.project_name = None
        self.pod_name = None
        self.installer = None
        self.version = None
        self.description = None
        self.creation_date = None
        self.details = None
        self.build_tag = None
        self.scenario = None
        self.criteria = None
        self.trust_indicator = None

    @staticmethod
    def from_dict(a_dict):

        if a_dict is None:
            return None

        t = TestResult()
        t._id = a_dict.get('_id')
        t.case_name = a_dict.get('case_name')
        t.pod_name = a_dict.get('pod_name')
        t.project_name = a_dict.get('project_name')
        t.description = a_dict.get('description')
        t.creation_date = str(a_dict.get('creation_date'))
        t.details = Details.from_dict(a_dict.get('details'))
        t.version = a_dict.get('version')
        t.installer = a_dict.get('installer')
        t.build_tag = a_dict.get('build_tag')
        t.scenario = a_dict.get('scenario')
        t.criteria = a_dict.get('criteria')
        # 0 < trust indicator < 1
        # if bad value =>  set this indicator to 0
        t.trust_indicator = a_dict.get('trust_indicator')
        if t.trust_indicator is not None:
            if isinstance(t.trust_indicator, (int, long, float)):
                if t.trust_indicator < 0:
                    t.trust_indicator = 0
                elif t.trust_indicator > 1:
                    t.trust_indicator = 1
            else:
                t.trust_indicator = 0
        else:
            t.trust_indicator = 0
        return t

    def format(self):
        return {
            "case_name": self.case_name,
            "project_name": self.project_name,
            "pod_name": self.pod_name,
            "description": self.description,
            "creation_date": str(self.creation_date),
            "version": self.version,
            "installer": self.installer,
            "details": self.details.format(),
            "build_tag": self.build_tag,
            "scenario": self.scenario,
            "criteria": self.criteria,
            "trust_indicator": self.trust_indicator
        }

    def format_http(self):
        return {
            "_id": str(self._id),
            "case_name": self.case_name,
            "project_name": self.project_name,
            "pod_name": self.pod_name,
            "description": self.description,
            "creation_date": str(self.creation_date),
            "version": self.version,
            "installer": self.installer,
            "details": self.details.format(),
            "build_tag": self.build_tag,
            "scenario": self.scenario,
            "criteria": self.criteria,
            "trust_indicator": self.trust_indicator
        }


class TestResults(object):
    def __init__(self, results=list()):
        self.results = results

    @staticmethod
    def from_dict(a_dict):
        if a_dict is None:
            return None

        res = TestResults()
        for result in a_dict.get('results'):
            res.results.append(TestResult.from_dict(result))
        return res
