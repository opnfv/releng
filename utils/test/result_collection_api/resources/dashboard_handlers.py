from tornado.web import HTTPError

from common.constants import HTTP_NOT_FOUND
from dashboard.dashboard_utils import check_dashboard_ready_project, \
    check_dashboard_ready_case, get_dashboard_result
from resources.result_handlers import GenericResultHandler
from resources.result_models import TestResult
from tornado_swagger_ui.tornado_swagger import swagger


class GenericDashboardHandler(GenericResultHandler):
    def __init__(self, application, request, **kwargs):
        super(GenericDashboardHandler, self).__init__(application,
                                                      request,
                                                      **kwargs)
        self.table = self.db_results
        self.table_cls = TestResult


class DashboardHandler(GenericDashboardHandler):
    @swagger.operation(nickname='query')
    def get(self):
        """
            @description: Retrieve dashboard ready result(s)
                          for a test project
            @notes: Retrieve dashboard ready result(s) for a test project
                Available filters for this request are :
                 - project : project name
                 - case : case name
                 - pod : pod name
                 - version : platform version (Arno-R1, ...)
                 - installer (fuel, ...)
                 - period : x (x last days)

                GET /dashboard?project=functest&case=vPing&version=Colorado \
                &pod=pod_name&period=15
            @rtype: L{string}
            @param pod: pod name
            @type pod: L{string}
            @in pod: query
            @required pod: False
            @param project: project name
            @type project: L{string}
            @in project: query
            @required project: True
            @param case: case name
            @type case: L{string}
            @in case: query
            @required case: True
            @param version: i.e. Colorado
            @type version: L{string}
            @in version: query
            @required version: False
            @param installer: fuel/apex/joid/compass
            @type installer: L{string}
            @in installer: query
            @required installer: False
            @param period: last days
            @type period: L{string}
            @in period: query
            @required period: False
            @return 200: test result exist
            @raise 400: period is not in
            @raise 404: project or case name missing,
                        or project or case is not dashboard ready
        """

        project_arg = self.get_query_argument("project", None)
        case_arg = self.get_query_argument("case", None)

        # on /dashboard retrieve the list of projects and testcases
        # ready for dashboard
        if project_arg is None:
            raise HTTPError(HTTP_NOT_FOUND, "Project name missing")

        if not check_dashboard_ready_project(project_arg):
            raise HTTPError(HTTP_NOT_FOUND,
                            'Project [{}] not dashboard ready'
                            .format(project_arg))

        if case_arg is None:
            raise HTTPError(
                HTTP_NOT_FOUND,
                'Test case missing for project [{}]'.format(project_arg))

        if not check_dashboard_ready_case(project_arg, case_arg):
            raise HTTPError(
                HTTP_NOT_FOUND,
                'Test case [{}] not dashboard ready for project [{}]'
                .format(case_arg, project_arg))

        # special case of status for project
        if case_arg == 'status':
            self.finish_request(get_dashboard_result(project_arg, case_arg))
        else:
            def get_result(res, project, case):
                return get_dashboard_result(project, case, res)

            self._list(self.set_query(), get_result, project_arg, case_arg)
