import unittest
from tornado.web import Application
from tornado import gen
from tornado.testing import AsyncHTTPTestCase, gen_test

import fake_pymongo


class MyTest(AsyncHTTPTestCase):
    def setUp(self):
        super(MyTest, self).setUp()
        self.db = fake_pymongo
        self.io_loop.run_sync(self.fixture_setup)

    def get_app(self):
        return Application()

    @gen.coroutine
    def fixture_setup(self):
        self.test1 = {'_id': '1', 'name': 'test1'}
        self.test2 = {'name': 'test2'}
        yield self.db.pods.insert({'_id': '1', 'name': 'test1'})
        yield self.db.pods.insert({'name': 'test2'})

    @gen_test
    def test_find_one(self):
        user = yield self.db.pods.find_one({'name': 'test1'})
        self.assertEqual(user, self.test1)

    @gen_test
    def test_find(self):
        cursor = self.db.pods.find()
        names = []
        while (yield cursor.fetch_next):
            ob = cursor.next_object()
            names.append(ob.get('name'))
        self.assertItemsEqual(names, ['test1', 'test2'])

    @gen_test
    def test_update(self):
        yield self.db.pods.update({'_id': '1'}, {'name': 'new_test1'})
        user = yield self.db.pods.find_one({'_id': '1'})
        self.assertEqual(user.get('name', None), 'new_test1')

    @gen_test
    def test_remove(self):
        yield self.db.pods.remove({'_id': '1'})
        user = yield self.db.pods.find_one({'_id': '1'})
        self.assertIsNone(user)

if __name__ == '__main__':
    unittest.main()
