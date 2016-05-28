from datetime import datetime, timedelta

from bson.objectid import ObjectId
from tornado.web import HTTPError

from common.constants import HTTP_BAD_REQUEST, HTTP_NOT_FOUND
from resources.handlers import GenericApiHandler
from resources.result_models import TestResult
from tornado_swagger_ui.tornado_swagger import swagger


class GenericResultHandler(GenericApiHandler):
    def __init__(self, application, request, **kwargs):
        super(GenericResultHandler, self).__init__(application,
                                                   request,
                                                   **kwargs)
        self.table = self.db_results
        self.table_cls = TestResult


class ResultsCLHandler(GenericResultHandler):
    @swagger.operation(nickname="list-all")
    def get(self):
        """
            @description: list all test results consist with query
            @return 200: all test results consist with query,
                         empty list if no result is found
            @rtype: L{TestResults}
        """
        query = dict()
        pod_arg = self.get_query_argument("pod", None)
        project_arg = self.get_query_argument("project", None)
        case_arg = self.get_query_argument("case", None)
        version_arg = self.get_query_argument("version", None)
        installer_arg = self.get_query_argument("installer", None)
        build_tag_arg = self.get_query_argument("build_tag", None)
        scenario_arg = self.get_query_argument("scenario", None)
        criteria_arg = self.get_query_argument("criteria", None)
        period_arg = self.get_query_argument("period", None)
        trust_indicator_arg = self.get_query_argument("trust_indicator", None)

        if project_arg is not None:
            query["project_name"] = project_arg

        if case_arg is not None:
            query["case_name"] = case_arg

        if pod_arg is not None:
            query["pod_name"] = pod_arg

        if version_arg is not None:
            query["version"] = version_arg

        if installer_arg is not None:
            query["installer"] = installer_arg

        if build_tag_arg is not None:
            query["build_tag"] = build_tag_arg

        if scenario_arg is not None:
            query["scenario"] = scenario_arg

        if criteria_arg is not None:
            query["criteria_tag"] = criteria_arg

        if trust_indicator_arg is not None:
            query["trust_indicator_arg"] = trust_indicator_arg

        if period_arg is not None:
            try:
                period_arg = int(period_arg)
            except:
                raise HTTPError(HTTP_BAD_REQUEST)

            if period_arg > 0:
                period = datetime.now() - timedelta(days=period_arg)
                obj = {"$gte": str(period)}
                query["creation_date"] = obj

        self._list(query)

    @swagger.operation(nickname="create")
    def post(self):
        """
            @description: create a test result
            @param body: result to be created
            @type body: L{ResultCreateRequest}
            @in body: body
            @rtype: L{TestResult}
            @return 200: result is created.
            @raise 404: pod/project/testcase not exist
            @raise 400: body/pod_name/project_name/case_name not provided
        """
        def pod_query(data):
            return {'name': data.pod_name}

        def pod_error(data):
            message = 'Could not find pod [{}]'.format(data.pod_name)
            return HTTP_NOT_FOUND, message

        def project_query(data):
            return {'name': data.project_name}

        def project_error(data):
            message = 'Could not find project [{}]'.format(data.project_name)
            return HTTP_NOT_FOUND, message

        def testcase_query(data):
            return {'project_name': data.project_name, 'name': data.case_name}

        def testcase_error(data):
            message = 'Could not find testcase [{}] in project [{}]'\
                .format(data.case_name, data.project_name)
            return HTTP_NOT_FOUND, message

        miss_checks = ['pod_name', 'project_name', 'case_name']
        db_checks = [('pods', True, pod_query, pod_error),
                     ('projects', True, project_query, project_error),
                     ('testcases', True, testcase_query, testcase_error)]
        self._create(miss_checks, db_checks)


class ResultsGURHandler(GenericResultHandler):
    @swagger.operation(nickname='get-one')
    def get(self, result_id):
        """
            @description: get a single result by result_id
            @rtype: L{TestResult}
            @return 200: test result exist
            @raise 404: test result not exist
        """
        query = dict()
        query["_id"] = ObjectId(result_id)
        self._get_one(query)
