##############################################################################
# Copyright (c) 2015 Orange
# guyrodrigue.koffi@orange.com / koffirodrigue@gmail.com
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

"""
Pre-requisites:
    pip install motor
    pip install tornado

We can launch the API with this file

TODOs :
  - logging
  - json args validation with schemes
  - POST/PUT/DELETE for PODs
  - POST/PUT/GET/DELETE for installers, platforms (enrich results info)
  - count cases for GET on projects
  - count results for GET on cases
  - include objects
  - swagger documentation
  - setup file
  - results pagination
  - unit tests

"""

import argparse

import tornado.ioloop
import motor

from resources.handlers import VersionHandler, \
    TestResultsHandler, DashboardHandler
from resources.testcase_handlers import TestcaseCLHandler, TestcaseGURHandler
from resources.pod_handlers import PodCLHandler, PodGURHandler
from resources.project_handlers import ProjectCLHandler, ProjectGURHandler
from common.config import APIConfig
from tornado_swagger_ui.tornado_swagger import swagger

# optionally get config file from command line
parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config-file", dest='config_file',
                    help="Config file location")
args = parser.parse_args()
CONF = APIConfig().parse(args.config_file)

# connecting to MongoDB server, and choosing database
client = motor.MotorClient(CONF.mongo_url)
db = client[CONF.mongo_dbname]


def make_app():
    return swagger.Application(
        [
            # GET /version => GET API version
            (r"/versions", VersionHandler),

            # few examples:
            # GET /api/v1/pods => Get all pods
            # GET /api/v1/pods/1 => Get details on POD 1
            (r"/api/v1/pods", PodCLHandler),
            (r"/api/v1/pods/([^/]+)", PodGURHandler),

            # few examples:
            # GET /projects
            # GET /projects/yardstick
            (r"/api/v1/projects", ProjectCLHandler),
            (r"/api/v1/projects/([^/]+)", ProjectGURHandler),

            # few examples
            # GET /projects/qtip/cases => Get cases for qtip
            (r"/api/v1/projects/([^/]+)/cases", TestcaseCLHandler),
            (r"/api/v1/projects/([^/]+)/cases/([^/]+)", TestcaseGURHandler),

            # new path to avoid a long depth
            # GET /results?project=functest&case=keystone.catalog&pod=1
            #   => get results with optional filters
            # POST /results =>
            # Push results with mandatory request payload parameters
            # (project, case, and pod)
            (r"/api/v1/results", TestResultsHandler),
            (r"/api/v1/results([^/]*)", TestResultsHandler),
            (r"/api/v1/results/([^/]*)", TestResultsHandler),

            # Method to manage Dashboard ready results
            # GET /dashboard?project=functest&case=vPing&pod=opnfv-jump2
            #  => get results in dasboard ready format
            # get /dashboard
            #  => get the list of project with dashboard ready results
            (r"/dashboard/v1/results", DashboardHandler),
            (r"/dashboard/v1/results([^/]*)", DashboardHandler),
        ],
        db=db,
        debug=CONF.api_debug_on,
    )


def main():
    application = make_app()
    application.listen(CONF.api_port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
