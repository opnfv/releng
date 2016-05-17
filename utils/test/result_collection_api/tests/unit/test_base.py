from tornado.web import Application
from tornado.testing import AsyncHTTPTestCase

from resources.handlers import VersionHandler, PodHandler, \
    TestProjectHandler, TestCasesHandler, TestResultsHandler, DashboardHandler
import fake_pymongo


class TestBase(AsyncHTTPTestCase):
    def get_app(self):
        return Application(
            [
                (r"/version", VersionHandler),
                (r"/pods", PodHandler),
                (r"/pods/([^/]+)", PodHandler),
                (r"/test_projects", TestProjectHandler),
                (r"/test_projects/([^/]+)", TestProjectHandler),
                (r"/test_projects/([^/]+)/cases", TestCasesHandler),
                (r"/test_projects/([^/]+)/cases/([^/]+)", TestCasesHandler),
                (r"/results", TestResultsHandler),
                (r"/results([^/]*)", TestResultsHandler),
                (r"/results/([^/]*)", TestResultsHandler),
                (r"/dashboard", DashboardHandler),
                (r"/dashboard([^/]*)", DashboardHandler),
                (r"/dashboard/([^/]*)", DashboardHandler),
            ],
            db=fake_pymongo,
            debug=True,
        )

    def tearDown(self):
        yield fake_pymongo.pod.remove()
        yield fake_pymongo.test_projects.remove()
        yield fake_pymongo.test_cases.remove()
        yield fake_pymongo.test_results.remove()
        super(TestBase, self).tearDown()
