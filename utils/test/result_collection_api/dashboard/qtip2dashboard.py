#!/usr/bin/python

##############################################################################
# Copyright (c) 2015 Dell Inc  and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################


def get_qtip_cases():
    """
    get the list of the supported test cases
    TODO: update the list when adding a new test case for the dashboard
    """
    return ["compute_test_suite","storage_test_suite","network_test_suite"]


def check_qtip_case_exist(case):
    """
    check if the testcase exists
    if the test case is not defined or not declared in the list
    return False
    """
    qtip_cases = get_qtip_cases()
 
    if (case is None or case not in qtip_cases):
        return False
    else:
        return True


def format_qtip_for_dashboard(case, results):
    """
    generic method calling the method corresponding to the test case
    check that the testcase is properly declared first
    then build the call to the specific method
    """
    if check_qtip_case_exist(case):
        res = format_common_for_dashboard(case, results)
    else:
        res = []
        print "Test cases not declared"
    return res

def format_common_for_dashboard(case, results):
    """
    Common post processing
    """
    test_data_description = case + " results for Dashboard"
    test_data = [{'description': test_data_description}]

    graph_name = ''
    if "network_test_suite" in case:
        graph_name = "Throughput index"
    else:
        graph_name = "Index"

    # Graph 1: Rx fps = f(time)
    # ********************************
    new_element = []
    for data in results:
        new_element.append({'x': data['creation_date'],
                            'y1': data['details']['index'],
                            })

    test_data.append({'name': graph_name,
                      'info': {'type': "graph",
                               'xlabel': 'time',
                               'y1label': 'Index Number'},
                      'data_set': new_element})

    return test_data




############################  For local test  ################################
import os

def _test():
    ans = [{'creation_date': '2015-09-12', 'project_name': 'qtip', 'version': 'test', 'pod_name': 'dell-us-testing-1', 'case_name': 'compute_test_suite', 'installer': 'fuel', 'details': {'index': '0.9'}},
           {'creation_date': '2015-09-33', 'project_name': 'qtip', 'version': 'test', 'pod_name': 'dell-us-testing-1', 'case_name': 'compute_test_suite', 'installer': 'fuel', 'details': {'index': '0.8'}}]

    result = format_qtip_for_dashboard("compute_test_suite", ans)
    print result

    result = format_qtip_for_dashboard("storage_test_suite", ans)
    print result

    result = format_qtip_for_dashboard("network_test_suite", ans)
    print result

if __name__ == '__main__':
    _test()