#!/usr/bin/python
#
# Copyright (c) 2015 Orange
# morgan.richomme@orange.com
#
# This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# This script is used to build dashboard ready json results
# It may be used for all the test case of the Functest project
# a new method format_<Test_case>_for_dashboard(results)
# v0.1: basic example with methods for odl, Tempest, Rally and vPing
#


def get_functest_cases():
    """
    get the list of the supported test cases
    TODO: update the list when adding a new test case for the dashboard
    """
    return ["vPing", "Tempest", "odl", "Rally"]


def format_functest_for_dashboard(case, results):
    """
    generic method calling the method corresponding to the test case
    check that the testcase is properly declared first
    then build the call to the specific method
    """
    if check_functest_case_exist(case):
        cmd = "format_" + case + "_for_dashboard(results)"
        res = eval(cmd)
    else:
        res = []
        print "Test cases not declared"
    return res


def check_functest_case_exist(case):
    """
    check if the testcase exists
    if the test case is not defined or not declared in the list
    return False
    """
    functest_cases = get_functest_cases()

    if (case is None or case not in functest_cases):
        return False
    else:
        return True


def format_Tempest_for_dashboard(results):
    """
    Post processing for the Tempest test case
    """
    test_data = [{'description': 'Tempest results for Dashboard'}]
    return test_data


def format_odl_for_dashboard(results):
    """
    Post processing for the odl test case
    """
    test_data = [{'description': 'odl results for Dashboard'}]
    return test_data


def format_Rally_for_dashboard(results):
    """
    Post processing for the Rally test case
    """
    test_data = [{'description': 'Rally results for Dashboard'}]
    return test_data


def format_vPing_for_dashboard(results):
    """
    Post processing for the vPing test case
    """
    test_data = [{'description': 'vPing results for Dashboard'}]

    # Graph 1: Test_Duration = f(time)
    # ********************************
    new_element = []
    for data in results:
        new_element.append({'x': data['creation_date'],
                            'y': data['details']['duration']})

    test_data.append({'name': "vPing duration",
                      'info': {'type': "graph",
                               'xlabel': 'time',
                               'ylabel': 'duration (s)'},
                      'data_set': new_element})

    # Graph 2: bar
    # ************
    nbTest = 0
    nbTestOk = 0

    for data in results:
        nbTest += 1
        if data['details']['status'] == "OK":
            nbTestOk += 1

    test_data.append({'name': "vPing status",
                      'info': {"type": "bar"},
                      'data_set': [{'Nb tests': nbTest,
                                    'Nb Success': nbTestOk}]})

    return test_data
