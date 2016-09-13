#!/usr/bin/env python
#
# feng.xiaowei@zte.com.cn
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Logging levels:
#  Level     Numeric value
#  CRITICAL  50
#  ERROR     40
#  WARNING   30
#  INFO      20
#  DEBUG     10
#  NOTSET    0
#
# Usage:
#  import functest_logger as fl
#  logger = fl.Logger("script_name").getLogger()
#  logger.info("message to be shown with - INFO - ")
#  logger.debug("message to be shown with - DEBUG -")

import logging
import os


class Logger(object):
    file_path = '/var/log'
    formatter = logging.Formatter('%(asctime)s - %(name)s - '
                                  '%(levelname)s - %(message)s')

    def __init__(self, logger_name):

        IF_DEBUG = os.getenv('IF_DEBUG')

        self.logger_name = logger_name
        self.logger = logging.getLogger(logger_name)
        self.logger.propagate = 0
        self.logger.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        ch.setFormatter(self.formatter)
        if IF_DEBUG is not None and IF_DEBUG.lower() == "true":
            ch.setLevel(logging.DEBUG)
        else:
            ch.setLevel(logging.INFO)
        self.logger.addHandler(ch)

        hdlr = logging.FileHandler('%s/%s.log' % (self.file_path, logger_name))
        hdlr.setFormatter(self.formatter)
        hdlr.setLevel(logging.DEBUG)
        self.logger.addHandler(hdlr)

    @property
    def get(self):
        return self.logger


class KibanaDashboardLogger(Logger):
    file_path = '/var/log/kibana_dashboard'

    def __init__(self, logger_name):
        super(KibanaDashboardLogger, self).__init__(logger_name)

