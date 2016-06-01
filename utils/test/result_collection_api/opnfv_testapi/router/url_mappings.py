from opnfv_testapi.resources.handlers import VersionHandler
from opnfv_testapi.resources.testcase_handlers import TestcaseCLHandler, \
    TestcaseGURHandler
from opnfv_testapi.resources.pod_handlers import PodCLHandler, PodGURHandler
from opnfv_testapi.resources.project_handlers import ProjectCLHandler, \
    ProjectGURHandler
from opnfv_testapi.resources.result_handlers import ResultsCLHandler, \
    ResultsGURHandler
from opnfv_testapi.resources.dashboard_handlers import DashboardHandler


mappings = [
    # GET /versions => GET API version
    (r"/versions", VersionHandler),

    # few examples:
    # GET /api/v1/pods => Get all pods
    # GET /api/v1/pods/1 => Get details on POD 1
    (r"/api/v1/pods", PodCLHandler),
    (r"/api/v1/pods/([^/]+)", PodGURHandler),

    # few examples:
    # GET /projects
    # GET /projects/yardstick
    (r"/api/v1/projects", ProjectCLHandler),
    (r"/api/v1/projects/([^/]+)", ProjectGURHandler),

    # few examples
    # GET /projects/qtip/cases => Get cases for qtip
    (r"/api/v1/projects/([^/]+)/cases", TestcaseCLHandler),
    (r"/api/v1/projects/([^/]+)/cases/([^/]+)", TestcaseGURHandler),

    # new path to avoid a long depth
    # GET /results?project=functest&case=keystone.catalog&pod=1
    #   => get results with optional filters
    # POST /results =>
    # Push results with mandatory request payload parameters
    # (project, case, and pod)
    (r"/api/v1/results", ResultsCLHandler),
    (r"/api/v1/results/([^/]+)", ResultsGURHandler),

    # Method to manage Dashboard ready results
    # GET /dashboard?project=functest&case=vPing&pod=opnfv-jump2
    #  => get results in dasboard ready format
    # get /dashboard
    #  => get the list of project with dashboard ready results
    (r"/dashboard/v1/results", DashboardHandler),
]
