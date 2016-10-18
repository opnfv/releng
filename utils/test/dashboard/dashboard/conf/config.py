#! /usr/bin/env python

import urlparse
from ConfigParser import SafeConfigParser, NoOptionError


class ParseError(Exception):
    """
    Custom exception class for config file
    """

    def __init__(self, message):
        self.msg = message

    def __str__(self):
        return 'error parsing config file : %s' % self.msg


class APIConfig:
    """
    The purpose of this class is to load values correctly from the config file.
    Each key is declared as an attribute in __init__() and linked in parse()
    """

    def __init__(self):
        self._default_config_location = "/etc/dashboard/config.ini"
        self.es_url = 'http://localhost:9200'
        self.es_creds = None
        self.kibana_url = None
        self.js_path = None
        self.index_url = None

    def _get_str_parameter(self, section, param):
        try:
            return self._parser.get(section, param)
        except NoOptionError:
            raise ParseError("[%s.%s] parameter not found" % (section, param))

    def _get_int_parameter(self, section, param):
        try:
            return int(self._get_str_parameter(section, param))
        except ValueError:
            raise ParseError("[%s.%s] not an int" % (section, param))

    def _get_bool_parameter(self, section, param):
        result = self._get_str_parameter(section, param)
        if str(result).lower() == 'true':
            return True
        if str(result).lower() == 'false':
            return False

        raise ParseError(
            "[%s.%s : %s] not a boolean" % (section, param, result))

    @staticmethod
    def parse(config_location=None):
        obj = APIConfig()

        if config_location is None:
            config_location = obj._default_config_location

        obj._parser = SafeConfigParser()
        obj._parser.read(config_location)
        if not obj._parser:
            raise ParseError("%s not found" % config_location)

        # Linking attributes to keys from file with their sections
        obj.es_url = obj._get_str_parameter("elastic", "url")
        obj.es_creds = obj._get_str_parameter("elastic", "creds")
        obj.kibana_url = obj._get_str_parameter("kibana", "url")
        obj.js_path = obj._get_str_parameter("kibana", "js_path")
        index = obj._get_str_parameter("elastic", "index")
        obj.index_url = urlparse.urljoin(obj.es_url, index)

        return obj

    def __str__(self):
        return "elastic_url = %s \n" \
               "elastic_creds = %s \n" \
               "kibana_url = %s \n" \
               "index_url = %s \n" \
               "js_path = %s \n" % (self.es_url,
                                    self.es_creds,
                                    self.kibana_url,
                                    self.index_url,
                                    self.js_path)
