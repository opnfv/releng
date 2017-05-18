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
    prefix = settings.docs_settings.get('swagger_prefix', '/swagger')
    if prefix[-1] != '/':
        prefix += '/'

    def _path(suffix):
        return prefix + suffix
    return [
        tornado.web.URLSpec(
            _path(r'spec.html$'),
            views.SwaggerUIHandler,
            settings.docs_settings,
            name=settings.API_DOCS_NAME),
        tornado.web.URLSpec(
            _path(r'resources.json$'),
            views.SwaggerResourcesHandler,
            settings.docs_settings,
            name=settings.RESOURCE_LISTING_NAME),
        tornado.web.URLSpec(
            _path(r'APIs$'),
            views.SwaggerApiHandler,
            settings.docs_settings,
            name=settings.API_DECLARATION_NAME),
    ]
