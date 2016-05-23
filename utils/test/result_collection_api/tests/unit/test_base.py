import json
from tornado.web import Application
from tornado.testing import AsyncHTTPTestCase

from resources.handlers import VersionHandler, PodHandler, \
    ProjectHandler, TestcaseHandler, TestResultsHandler, DashboardHandler
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
                (r"/projects", ProjectHandler),
                (r"/projects/([^/]+)", ProjectHandler),
                (r"/projects/([^/]+)/cases", TestcaseHandler),
                (r"/projects/([^/]+)/cases/([^/]+)", TestcaseHandler),
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

    def create_d(self, *args):
        return self.create(self.req_d, *args)

    def create_e(self, *args):
        return self.create(self.req_e, *args)

    def create(self, req=None, *args):
        return self.create_help(self.basePath, req, *args)

    def create_help(self, uri, req, *args):
        if req:
            req = req.format()
        res = self.fetch(self._update_uri(uri, *args),
                         method='POST',
                         body=json.dumps(req),
                         headers=self.headers)

        return self._get_return(res, self.create_res)

    def get(self, *args):
        res = self.fetch(self._get_uri(*args),
                         method='GET',
                         headers=self.headers)

        def inner():
            new_args, num = self._get_valid_args(*args)
            return self.get_res \
                if num != self._need_arg_num(self.basePath) else self.list_res
        return self._get_return(res, inner())

    def query(self, query):
        res = self.fetch(self._get_query_uri(query),
                         method='GET',
                         headers=self.headers)
        return self._get_return(res, self.list_res)

    def update(self, new=None, *args):
        if new:
            new = new.format()
        res = self.fetch(self._get_uri(*args),
                         method='PUT',
                         body=json.dumps(new),
                         headers=self.headers)
        return self._get_return(res, self.update_res)

    def delete(self, *args):
        res = self.fetch(self._get_uri(*args),
                         method='DELETE',
                         headers=self.headers)
        return res.code, res.body

    @staticmethod
    def _get_valid_args(*args):
        new_args = tuple(['%s' % arg for arg in args if arg is not None])
        return new_args, len(new_args)

    def _need_arg_num(self, uri):
        return uri.count('%s')

    def _get_query_uri(self, query):
        return self.basePath + '?' + query

    def _get_uri(self, *args):
        return self._update_uri(self.basePath, *args)

    def _update_uri(self, uri, *args):
        r_uri = uri
        new_args, num = self._get_valid_args(*args)
        if num != self._need_arg_num(uri):
            r_uri += '/%s'

        return r_uri % tuple(['%s' % arg for arg in new_args])

    def _get_return(self, res, cls):
        code = res.code
        body = res.body
        return code, self._get_return_body(code, body, cls)

    @staticmethod
    def _get_return_body(code, body, cls):
        return cls.from_dict(json.loads(body)) if code < 300 else body

    def assert_href(self, body):
        self.assertIn(self.basePath, body.href)

    def assert_create_body(self, body, req=None, *args):
        if not req:
            req = self.req_d
        new_args = args + tuple([req.name])
        self.assertIn(self._get_uri(*new_args), body.href)

    @staticmethod
    def _clear():
        fake_pymongo.pods.clear()
        fake_pymongo.projects.clear()
        fake_pymongo.testcases.clear()
        fake_pymongo.results.clear()
