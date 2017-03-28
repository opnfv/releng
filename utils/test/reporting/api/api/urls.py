##############################################################################
# Copyright (c) 2016 Huawei Technologies Co.,Ltd and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
from api.handlers import landing
from api.handlers import projects
from api.handlers import testcases

mappings = [
    (r"/landing-page/filters", landing.FiltersHandler),
    (r"/landing-page/scenarios", landing.ScenariosHandler),

    (r"/projects-page/projects", projects.Projects),
    (r"/projects/([^/]+)/cases", testcases.TestCases),
    (r"/projects/([^/]+)/cases/([^/]+)", testcases.TestCase)
]
