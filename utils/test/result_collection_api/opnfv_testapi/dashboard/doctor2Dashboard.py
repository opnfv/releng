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
# It may be used for all the test case of the Doctor project
# a new method format_<Test_case>_for_dashboard(results)
#
import re
import datetime


def get_doctor_cases():
    """
    get the list of the supported test cases
    TODO: update the list when adding a new test case for the dashboard
    """
    return ["doctor-notification","doctor-mark-down"]


def format_doctor_for_dashboard(case, results):
    """
    generic method calling the method corresponding to the test case
    check that the testcase is properly declared first
    then build the call to the specific method
    """
    
    if check_doctor_case_exist(case):
        # note we add _case because testcase and project had the same name
        # TODO refactoring...looks fine at the beginning wit only 1 project
        # not very ugly now and clearly not optimized...
        cmd = "format_" + case.replace('-','_') + "_case_for_dashboard"
        res = globals()[cmd](results)
    else:
        res = []
    return res


def check_doctor_case_exist(case):
    """
    check if the testcase exists
    if the test case is not defined or not declared in the list
    return False
    """
    doctor_cases = get_doctor_cases()

    if (case is None or case not in doctor_cases):
        return False
    else:
        return True


def format_doctor_mark_down_case_for_dashboard(results):
    """
    Post processing for the doctor test case
    """
    test_data = [{'description': 'doctor-mark-down results for Dashboard'}]
    return test_data


def format_doctor_notification_case_for_dashboard(results):
    """
    Post processing for the doctor-notification test case
    """
    test_data = [{'description': 'doctor results for Dashboard'}]
    # Graph 1: (duration)=f(time)
    # ***************************************
    new_element = []

    # default duration 0:00:08.999904
    # consider only seconds => 09
    for data in results:
        t = data['details']['duration']
        new_element.append({'x': data['start_date'],
                            'y': t})

    test_data.append({'name': "doctor-notification duration ",
                      'info': {'type': "graph",
                               'xlabel': 'time (s)',
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

    test_data.append({'name': "doctor-notification status",
                      'info': {"type": "bar"},
                      'data_set': [{'Nb tests': nbTest,
                                    'Nb Success': nbTestOk}]})

    return test_data
