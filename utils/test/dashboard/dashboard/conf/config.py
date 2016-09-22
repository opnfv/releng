#! /usr/bin/env python

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
        self._default_config_location = "../etc/config.ini"
        self.elastic_url = 'http://localhost:9200'
        self.elastic_creds = None
        self.destination = 'elasticsearch'
        self.kibana_url = None
        self.is_js = True
        self.js_path = None

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
        obj.elastic_url = obj._get_str_parameter("elastic", "url")
        obj.elastic_creds = obj._get_str_parameter("elastic", "creds")
        obj.destination = obj._get_str_parameter("output", "destination")
        obj.kibana_url = obj._get_str_parameter("kibana", "url")
        obj.is_js = obj._get_bool_parameter("kibana", "js")
        obj.js_path = obj._get_str_parameter("kibana", "js_path")

        return obj

    def __str__(self):
        return "elastic_url = %s \n" \
               "elastic_creds = %s \n" \
               "destination = %s \n" \
               "kibana_url = %s \n" \
               "is_js = %s \n" \
               "js_path = %s \n" % (self.elastic_url,
                                        self.elastic_creds,
                                        self.destination,
                                        self.kibana_url,
                                        self.is_js,
                                        self.js_path)
