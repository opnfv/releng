##############################################################################
# Copyright (c) 2016 ZTE Corporation
# feng.xiaowei@zte.com.cn
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import unittest

from tornado import gen
from tornado import testing
from tornado import web

from opnfv_testapi.tests.unit import fake_pymongo


class MyTest(testing.AsyncHTTPTestCase):
    def setUp(self):
        super(MyTest, self).setUp()
        self.db = fake_pymongo
        self.addCleanup(self._clear)
        self.io_loop.run_sync(self.fixture_setup)

    def get_app(self):
        return web.Application()

    @gen.coroutine
    def fixture_setup(self):
        self.test1 = {'_id': '1', 'name': 'test1'}
        self.test2 = {'name': 'test2'}
        yield self.db.pods.insert({'_id': '1', 'name': 'test1'})
        yield self.db.pods.insert({'name': 'test2'})

    @testing.gen_test
    def test_find_one(self):
        user = yield self.db.pods.find_one({'name': 'test1'})
        self.assertEqual(user, self.test1)
        self.db.pods.remove()

    @testing.gen_test
    def test_find(self):
        cursor = self.db.pods.find()
        names = []
        while (yield cursor.fetch_next):
            ob = cursor.next_object()
            names.append(ob.get('name'))
        self.assertItemsEqual(names, ['test1', 'test2'])

    @testing.gen_test
    def test_update(self):
        yield self.db.pods.update({'_id': '1'}, {'name': 'new_test1'})
        user = yield self.db.pods.find_one({'_id': '1'})
        self.assertEqual(user.get('name', None), 'new_test1')

    def test_update_dot_error(self):
        self._update_assert({'_id': '1', 'name': {'1. name': 'test1'}},
                            'key 1. name must not contain .')

    def test_update_dot_no_error(self):
        self._update_assert({'_id': '1', 'name': {'1. name': 'test1'}},
                            None,
                            check_keys=False)

    def test_update_dollar_error(self):
        self._update_assert({'_id': '1', 'name': {'$name': 'test1'}},
                            'key $name must not start with $')

    def test_update_dollar_no_error(self):
        self._update_assert({'_id': '1', 'name': {'$name': 'test1'}},
                            None,
                            check_keys=False)

    @testing.gen_test
    def test_remove(self):
        yield self.db.pods.remove({'_id': '1'})
        user = yield self.db.pods.find_one({'_id': '1'})
        self.assertIsNone(user)

    def test_insert_dot_error(self):
        self._insert_assert({'_id': '1', '2. name': 'test1'},
                            'key 2. name must not contain .')

    def test_insert_dot_no_error(self):
        self._insert_assert({'_id': '1', '2. name': 'test1'},
                            None,
                            check_keys=False)

    def test_insert_dollar_error(self):
        self._insert_assert({'_id': '1', '$name': 'test1'},
                            'key $name must not start with $')

    def test_insert_dollar_no_error(self):
        self._insert_assert({'_id': '1', '$name': 'test1'},
                            None,
                            check_keys=False)

    def _clear(self):
        self.db.pods.clear()

    def _update_assert(self, docs, error=None, **kwargs):
        self._db_assert('update', error, {'_id': '1'}, docs, **kwargs)

    def _insert_assert(self, docs, error=None, **kwargs):
        self._db_assert('insert', error, docs, **kwargs)

    @testing.gen_test
    def _db_assert(self, method, error, *args, **kwargs):
        name_error = None
        try:
            yield self._eval_pods_db(method, *args, **kwargs)
        except NameError as err:
            name_error = err.args[0]
        finally:
            self.assertEqual(name_error, error)

    def _eval_pods_db(self, method, *args, **kwargs):
        table_obj = vars(self.db)['pods']
        return table_obj.__getattribute__(method)(*args, **kwargs)


if __name__ == '__main__':
    unittest.main()
