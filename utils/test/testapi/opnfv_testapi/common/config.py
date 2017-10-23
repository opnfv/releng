##############################################################################
# Copyright (c) 2015 Orange
# guyrodrigue.koffi@orange.com / koffirodrigue@gmail.com
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
# feng.xiaowei@zte.com.cn remove prepare_put_request            5-30-2016
##############################################################################
import ConfigParser
import argparse
import os
import sys


class Config(object):

    def __init__(self):
        self.config_file = '/etc/opnfv_testapi/config.ini'
        self._set_config_file()
        self._parse()
        self._parse_per_page()

    def _parse(self):
        if not os.path.exists(self.config_file):
            raise Exception("%s not found" % self.config_file)

        config = ConfigParser.RawConfigParser()
        config.read(self.config_file)
        self._parse_section(config)

    def _parse_section(self, config):
        [self._parse_item(config, section) for section in (config.sections())]

    def _parse_item(self, config, section):
        [setattr(self, '{}_{}'.format(section, k), self._parse_value(v))
         for k, v in config.items(section)]

    def _parse_per_page(self):
        if not hasattr(self, 'api_results_per_page'):
            self.api_results_per_page = 20

    @staticmethod
    def _parse_value(value):
        try:
            value = int(value)
        except Exception:
            if str(value).lower() == 'true':
                value = True
            elif str(value).lower() == 'false':
                value = False
        return value

    def _set_config_file(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-c", "--config-file", dest='config_file',
                            help="Config file location", metavar="FILE")
        args, _ = parser.parse_known_args(sys.argv)
        if hasattr(args, 'config_file') and args.config_file:
            self.config_file = args.config_file


CONF = Config()
