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
# It may be used for all the test case of the Promise project
# a new method format_<Test_case>_for_dashboard(results)
# v0.1: basic example with methods for odl, Tempest, Rally and vPing
#
import re
import datetime


def get_promise_cases():
    """
    get the list of the supported test cases
    TODO: update the list when adding a new test case for the dashboard
    """
    return ["promise"]


def format_promise_for_dashboard(case, results):
    """
    generic method calling the method corresponding to the test case
    check that the testcase is properly declared first
    then build the call to the specific method
    """
    if check_promise_case_exist(case):
        # note we add _case because testcase and project had the same name
        # TODO refactoring...looks fine at the beginning wit only 1 project
        # not very ugly now and clearly not optimized...
        cmd = "format_" + case + "_case_for_dashboard(results)"
        res = eval(cmd)
    else:
        res = []
        print "Test cases not declared"
    return res


def check_promise_case_exist(case):
    """
    check if the testcase exists
    if the test case is not defined or not declared in the list
    return False
    """
    promise_cases = get_promise_cases()

    if (case is None or case not in promise_cases):
        return False
    else:
        return True





def format_promise_case_for_dashboard(results):
    """
    Post processing for the promise test case
    """
    test_data = [{'description': 'Promise results for Dashboard'}]
    # Graph 1: (duration)=f(time)
    # ***************************************
    new_element = []

    # default duration 0:00:08.999904
    # consider only seconds => 09
    for data in results:
        t = data['details']['duration']
        new_element.append({'x': data['creation_date'],
                            'y': t})

    test_data.append({'name': "Promise duration ",
                      'info': {'type': "graph",
                               'xlabel': 'time (s)',
                               'ylabel': 'duration (s)'},
                      'data_set': new_element})

    # Graph 2: (Nb test, nb failure)=f(time)
    # ***************************************
    new_element = []

    for data in results:
        promise_results = data['details']
        new_element.append({'x': data['creation_date'],
                            'y1': promise_results['tests'],
                            'y2': promise_results['failures']})

    test_data.append({'name': "Promise nb tests/nb failures",
                      'info': {'type': "graph",
                               'xlabel': 'time',
                               'y1label': 'Number of tests',
                               'y2label': 'Number of failures'},
                      'data_set': new_element})

    return test_data
