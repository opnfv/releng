from cas import CASClient
from tornado import gen
from tornado import web

from opnfv_testapi.common import constants
from opnfv_testapi.common.config import CONF
from opnfv_testapi.db import api as dbapi
from opnfv_testapi.handlers import base_handlers


class SignBaseHandler(base_handlers.GenericApiHandler):
    def __init__(self, application, request, **kwargs):
        super(SignBaseHandler, self).__init__(application, request, **kwargs)
        self.table = 'users'
        self.cas_client = CASClient(version='2',
                                    server_url=CONF.lfid_cas_url,
                                    service_url='{}/{}'.format(
                                        CONF.ui_url,
                                        CONF.lfid_signin_return))


class SigninHandler(SignBaseHandler):
    def get(self):
        self.redirect(url=(self.cas_client.get_login_url()))


class SigninReturnHandler(SignBaseHandler):

    @web.asynchronous
    @gen.coroutine
    def get(self):
        ticket = self.get_query_argument('ticket', default=None)
        if ticket:
            (user, attrs, _) = self.cas_client.verify_ticket(ticket=ticket)
            login_user = {
                'user': user,
                'email': attrs.get('mail'),
                'fullname': attrs.get('field_lf_full_name'),
                'groups': constants.TESTAPI_USERS + attrs.get('group', [])
            }
            q_user = {'user': user}
            db_user = yield dbapi.db_find_one(self.table, q_user)
            if not db_user:
                dbapi.db_save(self.table, login_user)
            else:
                dbapi.db_update(self.table, q_user, login_user)

            self.clear_cookie(constants.TESTAPI_ID)
            self.set_secure_cookie(constants.TESTAPI_ID, user)

            self.redirect(url=CONF.ui_url)


class SignoutHandler(SignBaseHandler):
    def get(self):
        """Handle signout request."""
        self.clear_cookie(constants.TESTAPI_ID)
        logout_url = self.cas_client.get_logout_url(redirect_url=CONF.ui_url)
        self.redirect(url=logout_url)
