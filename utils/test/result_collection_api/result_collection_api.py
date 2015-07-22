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
"""

from resources.handlers import VersionHandler, PodHandler, TestProjectHandler, TestCasesHandler
from common.constants import API_LISTENING_PORT, MONGO_URL
import tornado.ioloop
import motor


""" connecting to MongoDB server, and choosing database """
db = motor.MotorClient(MONGO_URL).test_results_collection


def make_app():
    return tornado.web.Application(
        [
            (r"/version", VersionHandler),

            (r"/pods", PodHandler),
            (r"/pods/([0-9]*)", PodHandler),

            (r"/test_projects", TestProjectHandler),
            (r"/test_projects/(.*)", TestProjectHandler),

            (r"/test_projects/(.+)/cases", TestCasesHandler),
            (r"/test_projects/(.+)/cases/(.*)", TestCasesHandler),

        ],
        db=db,
        debug=True,
    )


def main():
    application = make_app()
    application.listen(API_LISTENING_PORT)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()
