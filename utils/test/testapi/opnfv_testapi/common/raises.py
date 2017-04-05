##############################################################################
# Copyright (c) 2017 ZTE Corp
# feng.xiaowei@zte.com.cn
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import httplib

from tornado import web


class Raiser(object):
    code = httplib.OK

    def __init__(self, reason):
        raise web.HTTPError(self.code, reason)


class BadRequest(Raiser):
    code = httplib.BAD_REQUEST


class Forbidden(Raiser):
    code = httplib.FORBIDDEN


class NotFound(Raiser):
    code = httplib.NOT_FOUND


class Unauthorized(Raiser):
    code = httplib.UNAUTHORIZED


class CodeTBD(object):
    def __init__(self, code, reason):
        raise web.HTTPError(code, reason)
