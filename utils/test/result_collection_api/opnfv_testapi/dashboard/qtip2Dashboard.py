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

    # Graph 1:
    # ********************************
    new_element = []
    for date, index in results:
        new_element.append({'x': date,
                            'y1': index,
                            })

    test_data.append({'name': graph_name,
                      'info': {'type': "graph",
                               'xlabel': 'time',
                               'y1label': 'Index Number'},
                      'data_set': new_element})

    return test_data


############################  For local test  ################################
import os
import requests
import json
from collections import defaultdict

def _get_results(db_url, testcase):

    testproject = testcase["project"]
    testcase = testcase["testcase"]
    resultarray = defaultdict()
    #header
    header = {'Content-Type': 'application/json'}
    #url
    url = db_url + "/results?project="+testproject+"&case="+testcase
    data = requests.get(url,header)
    datajson = data.json()
    for x in range(0, len(datajson['test_results'])):

        rawresults = datajson['test_results'][x]['details']
        index = rawresults['index']
        resultarray[str(datajson['test_results'][x]['start_date'])]=index

    return resultarray

def _test():

    db_url = "http://testresults.opnfv.org/testapi"
    raw_result = defaultdict()

    raw_result = _get_results(db_url, {"project": "qtip", "testcase": "compute_test_suite"})
    resultitems= raw_result.items()
    result = format_qtip_for_dashboard("compute_test_suite", resultitems)
    print result

    raw_result = _get_results(db_url, {"project": "qtip", "testcase": "storage_test_suite"})
    resultitems= raw_result.items()
    result = format_qtip_for_dashboard("storage_test_suite", resultitems)
    print result

    raw_result = _get_results(db_url, {"project": "qtip", "testcase": "network_test_suite"})
    resultitems= raw_result.items()
    result = format_qtip_for_dashboard("network_test_suite", resultitems)
    print result

if __name__ == '__main__':
    _test()
