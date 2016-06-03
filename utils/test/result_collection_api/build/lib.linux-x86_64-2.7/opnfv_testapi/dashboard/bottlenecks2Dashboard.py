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
import os
import requests
import json


def get_bottlenecks_cases():
    """
    get the list of the supported test cases
    TODO: update the list when adding a new test case for the dashboard
    """
    return ["rubbos", "tu1", "tu3"]


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

    # Graph 1:Rubbos maximal throughput
    # ********************************
    #new_element = []
    #for each_result in results:
    #    throughput_data = [record['throughput'] for record in each_result['details']]
    #    new_element.append({'x': each_result['start_date'],
    #                        'y': max(throughput_data)})

    #test_data.append({'name': "Rubbos max throughput",
    #                  'info': {'type': "graph",
    #                           'xlabel': 'time',
    #                           'ylabel': 'maximal throughput'},
    #                  'data_set': new_element})

    # Graph 2: Rubbos last record
    # ********************************
    new_element = []
    latest_result = results[-1]["details"]
    for data in latest_result:
        client_num = int(data["client"])
        throughput = int(data["throughput"])
        new_element.append({'x': client_num,
                            'y': throughput})
    test_data.append({'name': "Rubbos throughput vs client number",
                      'info': {'type': "graph",
                      'xlabel': 'client number',
                      'ylabel': 'throughput'},
                      'data_set': new_element})

    return test_data


def format_tu1_for_dashboard(results):
    test_data = [{'description': 'Tu-1 performance result'}]
    line_element = []
    bar_element = {}
    last_result = results[-1]["details"]
    for key in sorted(last_result):
        bandwith = last_result[key]["Bandwidth"]
        pktsize = int(key)
        line_element.append({'x': pktsize,
                             'y': bandwith * 1000})
        bar_element[key] = bandwith * 1000
    # graph1, line
    test_data.append({'name': "VM2VM max single directional throughput",
                      'info': {'type': "graph",
                               'xlabel': 'pktsize',
                               'ylabel': 'bandwith(kpps)'},
                      'data_set': line_element})
    # graph2, bar
    test_data.append({'name': "VM2VM max single directional throughput",
                      'info': {"type": "bar"},
                      'data_set': bar_element})
    return test_data


def format_tu3_for_dashboard(results):
    test_data = [{'description': 'Tu-3 performance result'}]
    new_element = []
    bar_element = {}
    last_result = results[-1]["details"]
    for key in sorted(last_result):
        bandwith = last_result[key]["Bandwidth"]
        pktsize = int(key)
        new_element.append({'x': pktsize,
                            'y': bandwith * 1000})
        bar_element[key] = bandwith * 1000
    # graph1, line
    test_data.append({'name': "VM2VM max bidirectional throughput",
                      'info': {'type': "graph",
                               'xlabel': 'pktsize',
                               'ylabel': 'bandwith(kpps)'},
                      'data_set': new_element})
    # graph2, bar
    test_data.append({'name': "VM2VM max single directional throughput",
                      'info': {"type": "bar"},
                      'data_set': bar_element})
    return test_data


############################  For local test  ################################

def _read_sample_output(filename):
    curr_path = os.path.dirname(os.path.abspath(__file__))
    output = os.path.join(curr_path, filename)
    with open(output) as f:
        sample_output = f.read()

    result = json.loads(sample_output)
    return result


# Copy form functest/testcases/Dashboard/dashboard_utils.py
# and did some minor modification for local test.
def _get_results(db_url, test_criteria):
    test_project = test_criteria["project"]
    testcase = test_criteria["testcase"]

    # Build headers
    headers = {'Content-Type': 'application/json'}

    # build the request
    # if criteria is all => remove criteria
    url = db_url + "/results?project=" + test_project + "&case=" + testcase

    # Send Request to Test DB
    myData = requests.get(url, headers=headers)

    # Get result as a json object
    myNewData = json.loads(myData.text)

    # Get results
    myDataResults = myNewData['test_results']
    return myDataResults

#only for local test
def _test():
    db_url = "http://testresults.opnfv.org/testapi"
    results = _get_results(db_url, {"project": "bottlenecks", "testcase": "rubbos"})
    test_result = format_rubbos_for_dashboard(results)
    print json.dumps(test_result, indent=4)

    results = _get_results(db_url, {"project": "bottlenecks", "testcase": "tu1"})
    #results = _read_sample_output("sample")
    #print json.dumps(results, indent=4)
    test_result = format_tu1_for_dashboard(results)
    print json.dumps(test_result, indent=4)
    results = _get_results(db_url, {"project": "bottlenecks", "testcase": "tu3"})
    test_result = format_tu3_for_dashboard(results)
    print json.dumps(test_result, indent=4)


if __name__ == '__main__':
    _test()

