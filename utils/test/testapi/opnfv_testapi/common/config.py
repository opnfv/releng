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
import os


class Config(object):
    CONFIG = None

    def __init__(self):
        self.file = self.CONFIG if self.CONFIG else self._default_config()
        self._parse()
        self._parse_per_page()
        self.static_path = os.path.join(
            os.path.dirname(os.path.normpath(__file__)),
            os.pardir,
            'static')

    def _parse(self):
        if not os.path.exists(self.file):
            raise Exception("%s not found" % self.file)

        config = ConfigParser.RawConfigParser()
        config.read(self.file)
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
        except:
            if str(value).lower() == 'true':
                value = True
            elif str(value).lower() == 'false':
                value = False
        return value

    @staticmethod
    def _default_config():
        is_venv = os.getenv('VIRTUAL_ENV')
        return os.path.join('/' if not is_venv else is_venv,
                            'etc/opnfv_testapi/config.ini')
