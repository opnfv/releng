##############################################################################
# Copyright (c) 2016 ZTE Corporation
# feng.xiaowei@zte.com.cn
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
collections_old2New = {
    'pod': 'pods',
    'test_projects': 'projects',
    'test_testcases': 'testcases',
    'test_results': 'results'
}

fields_old2New = {
    'test_results': [({}, {'creation_date': 'start_date'})]
}

docs_old2New = {
    'test_results': [
        ({'criteria': 'failed'}, {'criteria': 'FAILED'}),
        ({'criteria': 'passed'}, {'criteria': 'PASS'})
    ]
}
