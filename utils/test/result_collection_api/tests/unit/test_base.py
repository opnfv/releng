import json
from tornado.web import Application
from tornado.testing import AsyncHTTPTestCase

from resources.handlers import VersionHandler, PodHandler, \
    TestProjectHandler, TestCasesHandler, TestResultsHandler, DashboardHandler
from resources.models import CreateResponse
import fake_pymongo


class TestBase(AsyncHTTPTestCase):
    headers = {'Content-Type': 'application/json; charset=UTF-8'}

    def setUp(self):
        self.basePath = ''
        self.create_res = CreateResponse
        self.get_res = None
        self.list_res = None
        self.update_res = None
        self.req_d = None
        self.req_e = None
        self.addCleanup(self._clear)
        super(TestBase, self).setUp()

    def get_app(self):
        return Application(
            [
                (r"/version", VersionHandler),
                (r"/pods", PodHandler),
                (r"/pods/([^/]+)", PodHandler),
                (r"/projects", TestProjectHandler),
                (r"/projects/([^/]+)", TestProjectHandler),
                (r"/projects/([^/]+)/cases", TestCasesHandler),
                (r"/projects/([^/]+)/cases/([^/]+)", TestCasesHandler),
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

    def create_d(self):
        return self.create(self.req_d)

    def create_e(self):
        return self.create(self.req_e)

    def create(self, req=None):
        if req:
            req = req.format()

        res = self.fetch(self.basePath,
                         method='POST',
                         body=json.dumps(req),
                         headers=self.headers)

        return self._get_return(res, self.create_res)

    def get(self, item=None):
        res = self.fetch(self._get_uri(item),
                         method='GET',
                         headers=self.headers)

        def inner():
            return self.get_res if item else self.list_res
        return self._get_return(res, inner())

    def update(self, item, new=None):
        if new:
            new = new.format()
        res = self.fetch(self._get_uri(item),
                         method='PUT',
                         body=json.dumps(new),
                         headers=self.headers)
        return self._get_return(res, self.update_res)

    def delete(self, item):
        res = self.fetch(self._get_uri(item),
                         method='DELETE',
                         headers=self.headers)
        return res.code

    def _get_uri(self, item=None):
        uri = self.basePath
        if item:
            uri += '/{}'.format(item)
        return uri

    def _get_return(self, res, cls):
        code = res.code
        body = res.body
        return code, self._get_return_body(code, body, cls)

    @staticmethod
    def _get_return_body(code, body, cls):
        return cls.from_dict(json.loads(body)) if code < 300 else body

    def assert_create_body(self, body, req=None):
        print(body.href)
        if not req:
            req = self.req_d
        self.assertIn(self._get_uri(req.name), body.href)

    @staticmethod
    def _clear():
        fake_pymongo.pods.clear()
        fake_pymongo.projects.clear()
        fake_pymongo.test_cases.clear()
        fake_pymongo.test_results.clear()
