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
from functest2Dashboard import format_functest_for_dashboard, \
    check_functest_case_exist

# any project test project wishing to provide dashboard ready values
# must include at least 2 methods
# - format_<Project>_for_dashboard
# - check_<Project>_case_exist


def check_dashboard_ready_project(test_project, path):
    # Check that the first param corresponds to a project
    # for whoch dashboard processing is available
    subdirectories = os.listdir(path)
    for testfile in subdirectories:
        m = re.search('^(.*)(2Dashboard.py)$', testfile)
        if m:
            if (m.group(1) == test_project):
                return True
    return False


def check_dashboard_ready_case(project, case):
    cmd = "check_" + project + "_case_exist(case)"
    return eval(cmd)


def get_dashboard_cases(path):
    # Retrieve all the test cases that could provide
    # Dashboard ready graphs
    # look in the releng repo
    # search all the project2Dashboard.py files
    # we assume that dashboard processing of project <Project>
    # is performed in the <Project>2Dashboard.py file
    dashboard_test_cases = []
    subdirectories = os.listdir(path)
    for testfile in subdirectories:
        m = re.search('^(.*)(2Dashboard.py)$', testfile)
        if m:
            dashboard_test_cases.append(m.group(1))

    return dashboard_test_cases


def get_dashboard_result(project, case, results):
    # get the dashboard ready results
    # paramters are:
    # project: project name
    # results: array of raw results pre-filterded
    # according to the parameters of the request
    cmd = "format_" + project + "_for_dashboard(case,results)"
    res = eval(cmd)
    return res
