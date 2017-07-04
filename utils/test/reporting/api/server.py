##############################################################################
# Copyright (c) 2016 Huawei Technologies Co.,Ltd and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import tornado.ioloop
import tornado.web
from tornado.options import define
from tornado.options import options

from api.urls import mappings

define("port", default=8000, help="run on the given port", type=int)


def main():
    tornado.options.parse_command_line()
    application = tornado.web.Application(mappings)
    application.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
