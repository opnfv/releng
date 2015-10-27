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
# It may be used for all the test case of the Yardstick project
# a new method format_<Test_case>_for_dashboard(results)
# v0.1: basic example with methods for Ping, Iperf, Netperf, Pktgen,
#       Fio, Lmbench, Perf, Cyclictest.
#


def get_yardstick_cases():
    """
    get the list of the supported test cases
    TODO: update the list when adding a new test case for the dashboard
    """
    return ["Ping", "Iperf", "Netperf", "Pktgen", "Fio", "Lmbench",
            "Perf", "Cyclictest"]


def format_yardstick_for_dashboard(case, results):
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


def check_yardstick_case_exist(case):
    """
    check if the testcase exists
    if the test case is not defined or not declared in the list
    return False
    """
    yardstick_cases = get_yardstick_cases()

    if (case is None or case not in yardstick_cases):
        return False
    else:
        return True


def _get_test_status_bar(results):
    nbTest = 0
    nbTestOk = 0

    for data in results:
        nbTest += 1
        records = [record for record in data['details']
                          if "benchmark" in record
                             and record["benchmark"]["errors"] != ""]
        if len(records) == 0:
            nbTestOk += 1
    return nbTest, nbTestOk


def format_ping_for_dashboard(results):
    """
    Post processing for the Ping test case
    """
    test_data = [{'description': 'Ping results for Dashboard'}]

    # Graph 1: Test_Duration = f(time)
    # ********************************
    new_element = []
    for data in results:
        records = [record["benchmark"]["data"]["rtt"]
                    for record in data['details']
                        if "benchmark" in record]

        avg_rtt = sum(records) / len(records)
        new_element.append({'x': data['creation_date'],
                            'y': avg_rtt})

    test_data.append({'name': "ping duration",
                      'info': {'type': "graph",
                               'xlabel': 'time',
                               'ylabel': 'duration (s)'},
                      'data_set': new_element})

    # Graph 2: bar
    # ************
    nbTest, nbTestOk = _get_test_status_bar(results)

    test_data.append({'name': "ping status",
                      'info': {"type": "bar"},
                      'data_set': [{'Nb tests': nbTest,
                                    'Nb Success': nbTestOk}]})

    return test_data


def format_iperf_for_dashboard(results):
    """
    Post processing for the Iperf test case
    """
    test_data = [{'description': 'Iperf results for Dashboard'}]
    return test_data


def format_netperf_for_dashboard(results):
    """
    Post processing for the Netperf test case
    """
    test_data = [{'description': 'Netperf results for Dashboard'}]
    return test_data


def format_pktgen_for_dashboard(results):
    """
    Post processing for the Pktgen test case
    """
    test_data = [{'description': 'Pktgen results for Dashboard'}]
    return test_data


def format_fio_for_dashboard(results):
    """
    Post processing for the Fio test case
    """
    test_data = [{'description': 'Fio results for Dashboard'}]
    return test_data


def format_lmbench_for_dashboard(results):
    """
    Post processing for the Lmbench test case
    """
    test_data = [{'description': 'Lmbench results for Dashboard'}]
    return test_data


def format_perf_for_dashboard(results):
    """
    Post processing for the Perf test case
    """
    test_data = [{'description': 'Perf results for Dashboard'}]
    return test_data


def format_cyclictest_for_dashboard(results):
    """
    Post processing for the Cyclictest test case
    """
    test_data = [{'description': 'Cyclictest results for Dashboard'}]
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


############################  For local test  ################################
import json
import os

def _read_sample_output(filename):
    curr_path = os.path.dirname(os.path.abspath(__file__))
    output = os.path.join(curr_path, filename)
    with open(output) as f:
        sample_output = f.read()

    result = json.loads(sample_output)
    return result

def _test():
    result = _read_sample_output("ping.json")

    print format_ping_for_dashboard(result)

if __name__ == '__main__':
    _test()
