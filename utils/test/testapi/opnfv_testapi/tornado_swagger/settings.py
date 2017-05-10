##############################################################################
# Copyright (c) 2016 ZTE Corporation
# feng.xiaowei@zte.com.cn
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import os.path

API_DOCS_NAME = 'swagger-api-docs'
RESOURCE_LISTING_NAME = 'swagger-resource-listing'
API_DECLARATION_NAME = 'swagger-api-declaration'
STATIC_PATH = os.path.join(os.path.dirname(os.path.normpath(__file__)),
                           'static')

docs_settings = {
    'base_url': '',
    'static_path': STATIC_PATH,
    'swagger_prefix': '/swagger',
    'api_version': 'v1.0',
    'swagger_version': '1.2',
    'api_key': '',
    'enabled_methods': ['get', 'post', 'put', 'patch', 'delete'],
    'exclude_namespaces': [],
}

models = []
