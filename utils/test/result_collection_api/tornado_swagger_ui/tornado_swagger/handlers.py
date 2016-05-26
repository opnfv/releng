#!/usr/bin/python
# -*- coding: utf-8 -*-
from tornado.web import URLSpec, StaticFileHandler

from settings import default_settings, \
    SWAGGER_API_DOCS, SWAGGER_API_LIST, SWAGGER_API_SPEC
from views import SwaggerUIHandler, SwaggerResourcesHandler, SwaggerApiHandler

__author__ = 'serena'


def swagger_handlers():
    prefix = default_settings.get('swagger_prefix', '/swagger')
    if prefix[-1] != '/':
        prefix += '/'

    def _path(suffix):
        return prefix + suffix
    return [
        URLSpec(
            _path(r'spec.html$'),
            SwaggerUIHandler,
            default_settings,
            name=SWAGGER_API_DOCS),
        URLSpec(
            _path(r'spec.json$'),
            SwaggerResourcesHandler,
            default_settings,
            name=SWAGGER_API_LIST),
        URLSpec(
            _path(r'spec$'),
            SwaggerApiHandler,
            default_settings,
            name=SWAGGER_API_SPEC),
        (
            _path(r'(.*\.(css|png|gif|js))'),
            StaticFileHandler,
            {'path': default_settings.get('static_path')}),
    ]
