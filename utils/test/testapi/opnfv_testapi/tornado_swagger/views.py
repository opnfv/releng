##############################################################################
# Copyright (c) 2016 ZTE Corporation
# feng.xiaowei@zte.com.cn
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import inspect
import json

import tornado.template
import tornado.web

from opnfv_testapi.tornado_swagger import settings


def json_dumps(obj, pretty=False):
    return json.dumps(obj,
                      sort_keys=True,
                      indent=4,
                      separators=(',', ': ')) if pretty else json.dumps(obj)


class SwaggerUIHandler(tornado.web.RequestHandler):
    def initialize(self, **kwargs):
        self.static_path = kwargs.get('static_path')
        self.base_url = kwargs.get('base_url')

    def get_template_path(self):
        return self.static_path

    def get(self):
        resource_url = self.reverse_url(settings.RESOURCE_LISTING_NAME)
        discovery_url = self.base_url + resource_url
        self.render('swagger/index.html', discovery_url=discovery_url)


class SwaggerResourcesHandler(tornado.web.RequestHandler):
    def initialize(self, **kwargs):
        self.api_version = kwargs.get('api_version')
        self.swagger_version = kwargs.get('swagger_version')
        self.base_url = kwargs.get('base_url')
        self.exclude_namespaces = kwargs.get('exclude_namespaces')

    def get(self):
        self.set_header('content-type', 'application/json')
        resources = {
            'apiVersion': self.api_version,
            'swaggerVersion': self.swagger_version,
            'basePath': self.base_url,
            'apis': [{
                'path': self.reverse_url(settings.API_DECLARATION_NAME),
                'description': 'Restful APIs Specification'
            }]
        }

        self.finish(json_dumps(resources, self.get_arguments('pretty')))


class SwaggerApiHandler(tornado.web.RequestHandler):
    def initialize(self, **kwargs):
        self.api_version = kwargs.get('api_version')
        self.swagger_version = kwargs.get('swagger_version')
        self.base_url = kwargs.get('base_url')

    def get(self):
        self.set_header('content-type', 'application/json')
        apis = self.find_api(self.application.handlers)
        if apis is None:
            raise tornado.web.HTTPError(404)

        specs = {
            'apiVersion': self.api_version,
            'swaggerVersion': self.swagger_version,
            'basePath': self.base_url,
            'resourcePath': '/',
            'produces': ["application/json"],
            'apis': [self.__get_api_spec__(path, spec, operations)
                     for path, spec, operations in apis],
            'models': self.__get_models_spec(settings.models)
        }
        self.finish(json_dumps(specs, self.get_arguments('pretty')))

    def __get_models_spec(self, models):
        models_spec = {}
        for model in models:
            models_spec.setdefault(model.id, self.__get_model_spec(model))
        return models_spec

    @staticmethod
    def __get_model_spec(model):
        return {
            'description': model.summary,
            'id': model.id,
            'notes': model.notes,
            'properties': model.properties,
            'required': model.required
        }

    @staticmethod
    def __get_api_spec__(path, spec, operations):
        return {
            'path': path,
            'description': spec.handler_class.__doc__,
            'operations': [{
                'httpMethod': api.func.__name__.upper(),
                'nickname': api.nickname,
                'parameters': api.params.values(),
                'summary': api.summary,
                'notes': api.notes,
                'responseClass': api.responseClass,
                'responseMessages': api.responseMessages,
            } for api in operations]
        }

    @staticmethod
    def find_api(host_handlers):
        def get_path(url, args):
            return url % tuple(['{%s}' % arg for arg in args])

        def get_operations(cls):
            return [member.rest_api
                    for (_, member) in inspect.getmembers(cls)
                    if hasattr(member, 'rest_api')]

        for host, handlers in host_handlers:
            for spec in handlers:
                for (_, mbr) in inspect.getmembers(spec.handler_class):
                    if inspect.ismethod(mbr) and hasattr(mbr, 'rest_api'):
                        path = get_path(spec._path, mbr.rest_api.func_args)
                        operations = get_operations(spec.handler_class)
                        yield path, spec, operations
                        break
