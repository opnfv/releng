#!/usr/bin/env python

# Copyright (c) 2016 Orange and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0import requests
import unittest
import requests

from opnfv.utils import OPNFVExceptions


def base_function():
    raise OPNFVExceptions.TestDbNotReachable('Test database is not reachable')


def base_function_wrong():
    raise OPNFVExceptions.NotSelfDefinedException


def db_connectivity():
    url = 'http://testresults.opnfv2.org/test/api/v1/projects/functest/cases'
    r = requests.get(url)
    if r.status_code is not 200:
        raise OPNFVExceptions.TestDbNotReachable('Database not found')


def project_unknown():
    url = 'http://testresults.opnfv.org/test/api/v1/projects/functest2/cases'
    r = requests.get(url)
    if len(r.json()['testcases']) is 0:
        raise OPNFVExceptions.UnknownProject


class TestBasicRaise(unittest.TestCase):
    def test(self):
        with self.assertRaises(Exception) as context:
            base_function()
        self.assertTrue('Test database is not reachable' in context.exception)


class TestWrongRaise(unittest.TestCase):
    def test(self):
        try:
            base_function_wrong()
        except OPNFVExceptions.OPNFVException:
            assert(False)
        except AttributeError:
            assert(True)


class TestCaseDBNotReachable(unittest.TestCase):
    def test(self):
        with self.assertRaises(Exception) as context:
            db_connectivity()
        self.assertTrue('Database not found' in context.exception)


class TestUnkownProject(unittest.TestCase):
    def test(self):
        try:
            project_unknown()
        except OPNFVExceptions.TestDashboardError:
            # should not be there
            assert(False)
        except OPNFVExceptions.UnknownProject:
            assert(True)
        except Exception:
            assert(False)

if __name__ == '__main__':
    unittest.main()
