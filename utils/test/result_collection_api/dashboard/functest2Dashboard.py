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
    return ["status", "vPing", "vIMS", "Tempest", "odl", "Rally"]


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


def format_status_for_dashboard(results):
    test_data = [{'description': 'Functest status'}]

    # define magic equation for the status....
    # 5 suites: vPing, odl, Tempest, vIMS, Rally
    # Which overall KPI make sense...

    # TODO to be done and discussed
    testcases = get_functest_cases()
    test_data.append({'nb test suite(s) run': len(testcases)-1})
    # test_data.append({'nb test suite(s) failed':1})
    # test_data.append({'test suite run': ['vPing', 'tempest', 'vIMS' ]})
    # test_data.append({'average Openstack Tempest failure rate (%)': 10})
    # test_data.append({'average odl failure rate (%)': 10})

    return test_data


def format_vIMS_for_dashboard(results):
    """
    Post processing for the vIMS test case
    """
    test_data = [{'description': 'vIMS results for Dashboard'}]

    # Graph 1: (duration_deployment_orchestrator,
    #            duration_deployment_vnf,
    #             duration_test) = f(time)
    # ********************************
    new_element = []

    for data in results:
        new_element.append({'x': data['creation_date'],
                            'y1': data['details']['orchestrator']['duration'],
                            'y2': data['details']['vIMS']['duration'],
                            'y3': data['details']['sig_test']['duration']})

    test_data.append({'name': "Tempest nb tests/nb failures",
                      'info': {'type': "graph",
                               'xlabel': 'time',
                               'y1label': 'orchestation deployment duration',
                               'y2label': 'vIMS deployment duration',
                               'y3label': 'vIMS test duration'},
                      'data_set': new_element})

    # Graph 2: (Nb test, nb failure, nb skipped)=f(time)
    # **************************************************
    new_element = []

    for data in results:
        # Retrieve all the tests
        nbTests = 0
        nbFailures = 0
        nbSkipped = 0
        vIMS_test = data['details']['sig_test']['result']

        for data_test in vIMS_test:
            # Calculate nb of tests run and nb of tests failed
            # vIMS_results = get_vIMSresults(vIMS_test)
            # print vIMS_results
            if data_test['result'] == "Passed":
                nbTests += 1
            elif data_test['result'] == "Failed":
                nbFailures += 1
            elif data_test['result'] == "Skipped":
                nbSkipped += 1

        new_element.append({'x': data['creation_date'],
                            'y1': nbTests,
                            'y2': nbFailures,
                            'y3': nbSkipped})

    test_data.append({'name': "vIMS nb tests passed/failed/skipped",
                      'info': {'type': "graph",
                               'xlabel': 'time',
                               'y1label': 'Number of tests passed',
                               'y2label': 'Number of tests failed',
                               'y3label': 'Number of tests skipped'},
                      'data_set': new_element})

    # Graph 3: bar graph Summ(nb tests run), Sum (nb tests failed)
    # ********************************************************
    nbTests = 0
    nbFailures = 0

    for data in results:
        vIMS_test = data['details']['sig_test']['result']

        for data_test in vIMS_test:
            nbTestsOK = 0
            nbTestsKO = 0

            if data_test['result'] == "Passed":
                nbTestsOK += 1
            elif data_test['result'] == "Failed":
                nbTestsKO += 1

            nbTests += nbTestsOK + nbTestsKO
            nbFailures += nbTestsKO

    test_data.append({'name': "Total number of tests run/failure tests",
                      'info': {"type": "bar"},
                      'data_set': [{'Run': nbTests,
                                    'Failed': nbFailures}]})

    return test_data


def format_Tempest_for_dashboard(results):
    """
    Post processing for the Tempest test case
    """
    test_data = [{'description': 'Tempest results for Dashboard'}]

    # Graph 1: Test_Duration = f(time)
    # ********************************
    new_element = []
    for data in results:
        new_element.append({'x': data['creation_date'],
                            'y': data['details']['duration']})

    test_data.append({'name': "Tempest duration",
                      'info': {'type': "graph",
                               'xlabel': 'time',
                               'ylabel': 'duration (s)'},
                      'data_set': new_element})

    # Graph 2: (Nb test, nb failure)=f(time)
    # ***************************************
    new_element = []
    for data in results:
        new_element.append({'x': data['creation_date'],
                            'y1': data['details']['tests'],
                            'y2': data['details']['failures']})

    test_data.append({'name': "Tempest nb tests/nb failures",
                      'info': {'type': "graph",
                               'xlabel': 'time',
                               'y1label': 'Number of tests',
                               'y2label': 'Number of failures'},
                      'data_set': new_element})

    # Graph 3: bar graph Summ(nb tests run), Sum (nb tests failed)
    # ********************************************************
    nbTests = 0
    nbFailures = 0

    for data in results:
        nbTests += data['details']['tests']
        nbFailures += data['details']['failures']

    test_data.append({'name': "Total number of tests run/failure tests",
                      'info': {"type": "bar"},
                      'data_set': [{'Run': nbTests,
                                    'Failed': nbFailures}]})

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
