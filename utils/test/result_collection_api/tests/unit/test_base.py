import json
from tornado.web import Application
from tornado.testing import AsyncHTTPTestCase

from resources.handlers import VersionHandler, PodHandler, \
    TestProjectHandler, TestCasesHandler, TestResultsHandler, DashboardHandler
import fake_pymongo


class TestBase(AsyncHTTPTestCase):
    headers = {'Content-Type': 'application/json; charset=UTF-8'}

    def setUp(self):
        self.addCleanup(self._clear)
        super(TestBase, self).setUp()

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

    def create(self, uri, body=None):
        return self.fetch(uri,
                          method='POST',
                          body=json.dumps(body),
                          headers=self.headers)

    def get(self, uri):
        return self.fetch(uri,
                          method='GET',
                          headers=self.headers)

    @staticmethod
    def _clear():
        fake_pymongo.pod.clear()
        fake_pymongo.test_projects.clear()
        fake_pymongo.test_cases.clear()
        fake_pymongo.test_results.clear()
