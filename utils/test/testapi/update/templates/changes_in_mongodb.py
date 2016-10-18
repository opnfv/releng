##############################################################################
# Copyright (c) 2016 ZTE Corporation
# feng.xiaowei@zte.com.cn
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
# 09/06/2016: change for migration after refactoring
# 16/06/2016: Alignment of test name (JIRA: FUNCTEST-304)
##############################################################################
collections_old2New = {
    # 'pod': 'pods',
    # 'test_projects': 'projects',
    # 'test_testcases': 'testcases',
    # 'test_results': 'results'
}

fields_old2New = {
    # 'test_results': [({}, {'creation_date': 'start_date'})]
}

docs_old2New = {
    # 'test_results': [
    #    ({'criteria': 'failed'}, {'criteria': 'FAILED'}),
    #    ({'criteria': 'passed'}, {'criteria': 'PASS'})
    # ]
    # 'testcases': [
    #     ({'name': 'vPing'}, {'name': 'vping_ssh'}),
    #     ({'name': 'Tempest'}, {'name': 'tempest_smoke_serial'}),
    #     ({'name': 'Rally'}, {'name': 'rally_sanity'}),
    #     ({'name': 'ODL'}, {'name': 'odl'}),
    #     ({'name': 'vIMS'}, {'name': 'vims'}),
    #     ({'name': 'ONOS'}, {'name': 'onos'}),
    #     ({'name': 'vPing_userdata'}, {'name': 'vping_userdata'}),
    #     ({'name': 'ovno'}, {'name': 'ocl'})
    # ],
    # 'results': [
    #     ({'case_name': 'vPing'}, {'case_name': 'vping_ssh'}),
    #     ({'case_name': 'Tempest'}, {'case_name': 'tempest_smoke_serial'}),
    #     ({'case_name': 'Rally'}, {'case_name': 'rally_sanity'}),
    #     ({'case_name': 'ODL'}, {'case_name': 'odl'}),
    #     ({'case_name': 'vIMS'}, {'case_name': 'vims'}),
    #     ({'case_name': 'ONOS'}, {'case_name': 'onos'}),
    #     ({'case_name': 'vPing_userdata'}, {'case_name': 'vping_userdata'}),
    #     ({'case_name': 'ovno'}, {'case_name': 'ocl'})
    # ]
    'results': [
        ({'trust_indicator': 0},
         {'trust_indicator': {'current': 0, 'histories': []}})
    ]
}
