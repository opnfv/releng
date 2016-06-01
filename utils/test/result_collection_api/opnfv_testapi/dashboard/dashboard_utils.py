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
# This script is used to retieve data from test DB
# and format them into a json format adapted for a dashboard
#
# v0.1: basic example
#
import os
import re
import sys
from functest2Dashboard import format_functest_for_dashboard, \
    check_functest_case_exist
from yardstick2Dashboard import format_yardstick_for_dashboard, \
    check_yardstick_case_exist
from vsperf2Dashboard import format_vsperf_for_dashboard, \
    check_vsperf_case_exist
from bottlenecks2Dashboard import format_bottlenecks_for_dashboard, \
    check_bottlenecks_case_exist
from qtip2Dashboard import format_qtip_for_dashboard, \
    check_qtip_case_exist
from promise2Dashboard import format_promise_for_dashboard, \
    check_promise_case_exist
from doctor2Dashboard import format_doctor_for_dashboard, \
    check_doctor_case_exist

# any project test project wishing to provide dashboard ready values
# must include at least 2 methods
# - format_<Project>_for_dashboard
# - check_<Project>_case_exist


def check_dashboard_ready_project(test_project):
    # Check that the first param corresponds to a project
    # for whoch dashboard processing is available
    # print("test_project: %s" % test_project)
    project_module = 'opnfv_testapi.dashboard.'+test_project + '2Dashboard'
    return True if project_module in sys.modules else False


def check_dashboard_ready_case(project, case):
    cmd = "check_" + project + "_case_exist(case)"
    return eval(cmd)


def get_dashboard_cases():
    # Retrieve all the test cases that could provide
    # Dashboard ready graphs
    # look in the releng repo
    # search all the project2Dashboard.py files
    # we assume that dashboard processing of project <Project>
    # is performed in the <Project>2Dashboard.py file
    modules = []
    cp = re.compile('dashboard.*2Dashboard')
    for module in sys.modules:
        if re.match(cp, module):
            modules.append(module)

    return modules


def get_dashboard_result(project, case, results=None):
    # get the dashboard ready results
    # paramters are:
    # project: project name
    # results: array of raw results pre-filterded
    # according to the parameters of the request
    cmd = "format_" + project + "_for_dashboard(case,results)"
    res = eval(cmd)
    return res
