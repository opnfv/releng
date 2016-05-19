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

import tornado.ioloop
import motor
import argparse

from resources.handlers import VersionHandler, PodHandler, \
    TestProjectHandler, TestCasesHandler, TestResultsHandler, DashboardHandler
from common.config import APIConfig


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
    return tornado.web.Application(
        [
            # GET /version => GET API version
            (r"/version", VersionHandler),

            # few examples:
            # GET /pods => Get all pods
            # GET /pods/1 => Get details on POD 1
            (r"/pods", PodHandler),
            (r"/pods/([^/]+)", PodHandler),

            # few examples:
            # GET /projects
            # GET /projects/yardstick
            (r"/projects", TestProjectHandler),
            (r"/projects/([^/]+)", TestProjectHandler),

            # few examples
            # GET /projects/qtip/cases => Get cases for qtip
            #
            (r"/projects/([^/]+)/cases", TestCasesHandler),
            (r"/projects/([^/]+)/cases/([^/]+)", TestCasesHandler),
            # (r"/test_cases/([^/]+)", TestCasesHandler),

            # new path to avoid a long depth
            # GET /results?project=functest&case=keystone.catalog&pod=1
            #   => get results with optional filters
            # POST /results =>
            # Push results with mandatory request payload parameters
            # (project, case, and pod)
            (r"/results", TestResultsHandler),
            (r"/results([^/]*)", TestResultsHandler),
            (r"/results/([^/]*)", TestResultsHandler),

            # Method to manage Dashboard ready results
            # GET /dashboard?project=functest&case=vPing&pod=opnfv-jump2
            #  => get results in dasboard ready format
            # get /dashboard
            #  => get the list of project with dashboard ready results
            (r"/dashboard", DashboardHandler),
            (r"/dashboard([^/]*)", DashboardHandler),
            (r"/dashboard/([^/]*)", DashboardHandler),
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
