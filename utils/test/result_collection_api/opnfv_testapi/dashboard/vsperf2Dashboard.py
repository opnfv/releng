#!/usr/bin/python

# Copyright 2015 Intel Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License"),
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

def get_vsperf_cases():
    """
    get the list of the supported test cases
    TODO: update the list when adding a new test case for the dashboard
    """
    return ["tput_ovsdpdk", "tput_ovs",
            "b2b_ovsdpdk", "b2b_ovs",
            "tput_mod_vlan_ovsdpdk", "tput_mod_vlan_ovs",
            "cont_ovsdpdk", "cont_ovs",
            "pvp_cont_ovsdpdkuser", "pvp_cont_ovsdpdkcuse", "pvp_cont_ovsvirtio",
            "pvvp_cont_ovsdpdkuser", "pvvp_cont_ovsdpdkcuse", "pvvp_cont_ovsvirtio",
            "scalability_ovsdpdk", "scalability_ovs",
            "pvp_tput_ovsdpdkuser", "pvp_tput_ovsdpdkcuse", "pvp_tput_ovsvirtio",
            "pvp_b2b_ovsdpdkuser", "pvp_b2b_ovsdpdkcuse", "pvp_b2b_ovsvirtio",
            "pvvp_tput_ovsdpdkuser", "pvvp_tput_ovsdpdkcuse", "pvvp_tput_ovsvirtio",
            "pvvp_b2b_ovsdpdkuser", "pvvp_b2b_ovsdpdkcuse", "pvvp_b2b_ovsvirtio",
            "cpu_load_ovsdpdk", "cpu_load_ovs",
            "mem_load_ovsdpdk", "mem_load_ovs"]


def check_vsperf_case_exist(case):
    """
    check if the testcase exists
    if the test case is not defined or not declared in the list
    return False
    """
    vsperf_cases = get_vsperf_cases()
 
    if (case is None or case not in vsperf_cases):
        return False
    else:
        return True


def format_vsperf_for_dashboard(case, results):
    """
    generic method calling the method corresponding to the test case
    check that the testcase is properly declared first
    then build the call to the specific method
    """
    if check_vsperf_case_exist(case):
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
    if "b2b" in case:
        graph_name = "B2B frames"
    else:
        graph_name = "Rx frames per second"

    # Graph 1: Rx fps = f(time)
    # ********************************
    new_element = []
    for data in results:
        new_element.append({'x': data['start_date'],
                            'y1': data['details']['64'],
                            'y2': data['details']['128'],
                            'y3': data['details']['512'],
                            'y4': data['details']['1024'],
                            'y5': data['details']['1518']})

    test_data.append({'name': graph_name,
                      'info': {'type': "graph",
                               'xlabel': 'time',
                               'y1label': 'frame size 64B',
                               'y2label': 'frame size 128B',
                               'y3label': 'frame size 512B',
                               'y4label': 'frame size 1024B',
                               'y5label': 'frame size 1518B'},
                      'data_set': new_element})

    return test_data




############################  For local test  ################################
import os

def _test():
    ans = [{'start_date': '2015-09-12', 'project_name': 'vsperf', 'version': 'ovs_master', 'pod_name': 'pod1-vsperf', 'case_name': 'tput_ovsdpdk', 'installer': 'build_sie', 'details': {'64': '26.804', '1024': '1097.284', '512': '178.137', '1518': '12635.860', '128': '100.564'}},
           {'start_date': '2015-09-33', 'project_name': 'vsperf', 'version': 'ovs_master', 'pod_name': 'pod1-vsperf', 'case_name': 'tput_ovsdpdk', 'installer': 'build_sie', 'details': {'64': '16.804', '1024': '1087.284', '512': '168.137', '1518': '12625.860', '128': '99.564'}}]

    result = format_vsperf_for_dashboard("pvp_cont_ovsdpdkcuse", ans)
    print result

    result = format_vsperf_for_dashboard("b2b_ovsdpdk", ans)
    print result

    result = format_vsperf_for_dashboard("non_existing", ans)
    print result

if __name__ == '__main__':
    _test()
