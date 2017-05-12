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
import sys

import motor
import tornado.ioloop

from opnfv_testapi.common import config
from opnfv_testapi.router import url_mappings
from opnfv_testapi.tornado_swagger import swagger

CONF = None


def parse_config(argv=[]):
    global CONF
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config-file", dest='config_file',
                        help="Config file location")
    args = parser.parse_args(argv)
    if args.config_file:
        config.Config.CONFIG = args.config_file
    CONF = config.Config()


def get_db():
    return motor.MotorClient(CONF.mongo_url)[CONF.mongo_dbname]


def make_app():
    swagger.docs(base_url=CONF.swagger_base_url,
                 static_path=CONF.static_path)
    return swagger.Application(
        url_mappings.mappings,
        db=get_db(),
        debug=CONF.api_debug,
        auth=CONF.api_authenticate
    )


def main():
    parse_config(sys.argv[1:])
    application = make_app()
    application.listen(CONF.api_port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
