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

from opnfv_testapi.common.config import APIConfig
from opnfv_testapi.tornado_swagger import swagger
from opnfv_testapi.router import url_mappings

# optionally get config file from command line
parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config-file", dest='config_file',
                    help="Config file location")
args = parser.parse_args()
CONF = APIConfig().parse(args.config_file)

# connecting to MongoDB server, and choosing database
client = motor.MotorClient(CONF.mongo_url)
db = client[CONF.mongo_dbname]

swagger.docs(base_url=CONF.swagger_base_url)

def make_app():
    return swagger.Application(
        url_mappings.mappings,
        db=db,
        debug=CONF.api_debug_on,
    )


def main():
    application = make_app()
    application.listen(CONF.api_port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
