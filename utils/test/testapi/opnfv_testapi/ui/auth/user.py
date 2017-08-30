from tornado import gen
from tornado import web

from opnfv_testapi.common import constants as const, raises
from opnfv_testapi.db import api as dbapi
from opnfv_testapi.ui.auth import base


class ProfileHandler(base.BaseHandler):
    @web.asynchronous
    @gen.coroutine
    def get(self):
        testapi_id = self.get_secure_cookie(const.TESTAPI_ID)
        if testapi_id:
            try:
                user = yield dbapi.db_find_one(self.table, {'user': testapi_id})
                self.finish_request({
                    "user": user.get('user'),
                    "email": user.get('email'),
                    "fullname": user.get('fullname'),
                    "groups": user.get('groups')
                })
            except Exception:
                pass
        raises.Unauthorized('Unauthorized')
