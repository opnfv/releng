#!/usr/bin/python
#
##############################################################################
# Copyright (c) 2015 Huawei Technologies Co.,Ltd and other.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
#
# This script is used to build dashboard ready json results
# It may be used for all the test case of the Bottlenecks project
# a new method format_<Test_case>_for_dashboard(results)
# v0.1: basic example with methods for Rubbos.
#


def get_bottlenecks_cases():
    """
    get the list of the supported test cases
    TODO: update the list when adding a new test case for the dashboard
    """
    return ["rubbos"]


def check_bottlenecks_case_exist(case):
    """
    check if the testcase exists
    if the test case is not defined or not declared in the list
    return False
    """
    bottlenecks_cases = get_bottlenecks_cases()

    if case is None or case not in bottlenecks_cases:
        return False
    else:
        return True


def format_bottlenecks_for_dashboard(case, results):
    """
    generic method calling the method corresponding to the test case
    check that the testcase is properly declared first
    then build the call to the specific method
    """
    if check_bottlenecks_case_exist(case):
        cmd = "format_" + case + "_for_dashboard(results)"
        res = eval(cmd)
    else:
        res = []
        print "Test cases not declared"
    return res


def format_rubbos_for_dashboard(results):

    """
    Post processing for the Rubbos test case
    """
    test_data = [{'description': 'Rubbos results'}]

    # Graph 1:
    # ********************************
    new_element = []
    for each_result in results:
        throughput_data = [record['throughput'] for record in each_result['details']]
        new_element.append({'x': each_result['creation_date'],
                            'y': max(throughput_data)})

    test_data.append({'name': "Rubbos max throughput",
                      'info': {'type': "graph",
                               'xlabel': 'time',
                               'ylabel': 'maximal throughput'},
                      'data_set': new_element})
    return test_data


# for local test
import json


def _test():
    print('Post processing for the Rubbos test case begin<--')
    results = '[{"details":[{"client":200,"throughput":20},{"client":300,"throughput":50}],"project_name":' \
              '"bottlenecks","pod_name":"unknown-pod","version":"unknown","installer":"fuel","description":' \
              '"bottlenecks test cases result","_id":"56793f11514bc5068a345da4","creation_date":' \
              '"2015-12-22 12:16:17.131438","case_name":"rubbos"},{"details":[{"client":200,"throughput":25},' \
              '{"client":300,"throughput":52}],"project_name":"bottlenecks","pod_name":"unknown-pod","version":' \
              '"unknown","installer":"fuel","description":"bottlenecks test cases result","_id":' \
              '"56793f11514bc5068a345da4","creation_date":"2015-12-23 12:16:17.131438","case_name":"rubbos"}]'

    print("the output is:")
    print(format_rubbos_for_dashboard(json.loads(results)))
    print('Post processing for the Rubbos test case end<--')


if __name__ == '__main__':
    _test()
