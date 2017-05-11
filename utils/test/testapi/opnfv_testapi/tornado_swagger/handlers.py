##############################################################################
# Copyright (c) 2016 ZTE Corporation
# feng.xiaowei@zte.com.cn
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import tornado.web

from opnfv_testapi.tornado_swagger import settings
from opnfv_testapi.tornado_swagger import views


def swagger_handlers():
    prefix = settings.default_settings.get('swagger_prefix', '/swagger')
    if prefix[-1] != '/':
        prefix += '/'

    def _path(suffix):
        return prefix + suffix
    return [
        tornado.web.URLSpec(
            _path(r'spec.html$'),
            views.SwaggerUIHandler,
            settings.default_settings,
            name=settings.SWAGGER_API_DOCS),
        tornado.web.URLSpec(
            _path(r'resources.json$'),
            views.SwaggerResourcesHandler,
            settings.default_settings,
            name=settings.SWAGGER_RESOURCE_LISTING),
        tornado.web.URLSpec(
            _path(r'APIs$'),
            views.SwaggerApiHandler,
            settings.default_settings,
            name=settings.SWAGGER_API_DECLARATION),
        (
            _path(r'(.*\.(css|png|gif|js))'),
            tornado.web.StaticFileHandler,
            {'path': settings.default_settings.get('static_path')}),
    ]
