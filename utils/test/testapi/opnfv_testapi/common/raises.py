import httplib

from tornado import web


class Raise(object):
    code = httplib.OK

    def __init__(self, reason):
        raise web.HTTPError(self.code, reason)


class BadRequest(Raise):
    code = httplib.BAD_REQUEST


class Forbidden(Raise):
    code = httplib.FORBIDDEN


class NotFound(Raise):
    code = httplib.NOT_FOUND


class Unauthorized(Raise):
    code = httplib.UNAUTHORIZED


class CodeTBD(object):
    def __init__(self, code, reason):
        raise web.HTTPError(code, reason)
