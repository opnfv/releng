from tornado import gen
from tornado import web

from opnfv_testapi.common import raises
from opnfv_testapi.db import api as dbapi
from opnfv_testapi.ui.auth import base


class ProfileHandler(base.BaseHandler):
    @web.asynchronous
    @gen.coroutine
    def get(self):
        openid = self.get_secure_cookie('openid')
        if openid:
            try:
                user = yield dbapi.db_find_one(self.table, {'openid': openid})
                self.finish_request({
                    "openid": user.get('openid'),
                    "email": user.get('email'),
                    "fullname": user.get('fullname'),
                    "role": user.get('role', 'user')
                })
            except Exception:
                pass
        raises.Unauthorized('Unauthorized')
