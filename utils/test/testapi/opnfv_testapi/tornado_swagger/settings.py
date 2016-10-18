##############################################################################
# Copyright (c) 2016 ZTE Corporation
# feng.xiaowei@zte.com.cn
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import os.path

SWAGGER_VERSION = '1.2'
SWAGGER_API_DOCS = 'swagger-api-docs'
SWAGGER_API_LIST = 'swagger-api-list'
SWAGGER_API_SPEC = 'swagger-api-spec'
STATIC_PATH = os.path.join(os.path.dirname(os.path.normpath(__file__)),
                           'static')

default_settings = {
    'base_url': '',
    'static_path': STATIC_PATH,
    'swagger_prefix': '/swagger',
    'api_version': 'v1.0',
    'api_key': '',
    'enabled_methods': ['get', 'post', 'put', 'patch', 'delete'],
    'exclude_namespaces': [],
}

models = []


def basePath():
    return default_settings.get('base_url')
