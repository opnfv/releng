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


class ParseError(Exception):
    """
    Custom exception class for config file
    """

    def __init__(self, message):
        self.msg = message

    def __str__(self):
        return 'error parsing config file : %s' % self.msg


class APIConfig(object):
    """
    The purpose of this class is to load values correctly from the config file.
    Each key is declared as an attribute in __init__() and linked in parse()
    """

    def __init__(self):
        self._set_default_config()
        self.mongo_url = None
        self.mongo_dbname = None
        self.api_port = None
        self.api_debug_on = None
        self.api_authenticate_on = None
        self._parser = None
        self.swagger_base_url = None

    def _set_default_config(self):
        venv = os.getenv('VIRTUAL_ENV')
        self._default_config = os.path.join('/' if not venv else venv,
                                            'etc/opnfv_testapi/config.ini')

    def _get_parameter(self, section, param):
        try:
            return self._parser.get(section, param)
        except ConfigParser.NoOptionError:
            raise ParseError("No parameter: [%s.%s]" % (section, param))

    def _get_int_parameter(self, section, param):
        try:
            return int(self._get_parameter(section, param))
        except ValueError:
            raise ParseError("Not int: [%s.%s]" % (section, param))

    def _get_bool_parameter(self, section, param):
        result = self._get_parameter(section, param)
        if str(result).lower() == 'true':
            return True
        if str(result).lower() == 'false':
            return False

        raise ParseError(
            "Not boolean: [%s.%s : %s]" % (section, param, result))

    @staticmethod
    def parse(config_location=None):
        obj = APIConfig()

        if config_location is None:
            config_location = obj._default_config

        if not os.path.exists(config_location):
            raise ParseError("%s not found" % config_location)

        obj._parser = ConfigParser.SafeConfigParser()
        obj._parser.read(config_location)

        # Linking attributes to keys from file with their sections
        obj.mongo_url = obj._get_parameter("mongo", "url")
        obj.mongo_dbname = obj._get_parameter("mongo", "dbname")

        obj.api_port = obj._get_int_parameter("api", "port")
        obj.api_debug_on = obj._get_bool_parameter("api", "debug")
        obj.api_authenticate_on = obj._get_bool_parameter("api",
                                                          "authenticate")

        obj.swagger_base_url = obj._get_parameter("swagger", "base_url")

        return obj
