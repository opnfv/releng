##############################################################################
# Copyright (c) 2016 ZTE Corporation
# feng.xiaowei@zte.com.cn
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
from tornado.web import URLSpec, StaticFileHandler

from settings import default_settings, \
    SWAGGER_API_DOCS, SWAGGER_RESOURCE_LISTING, SWAGGER_API_DECLARATION
from views import SwaggerUIHandler, SwaggerResourcesHandler, SwaggerApiHandler


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
            _path(r'resources.json$'),
            SwaggerResourcesHandler,
            default_settings,
            name=SWAGGER_RESOURCE_LISTING),
        URLSpec(
            _path(r'APIs$'),
            SwaggerApiHandler,
            default_settings,
            name=SWAGGER_API_DECLARATION),
        (
            _path(r'(.*\.(css|png|gif|js))'),
            StaticFileHandler,
            {'path': default_settings.get('static_path')}),
    ]
