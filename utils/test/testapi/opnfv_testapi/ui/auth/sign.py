from cas import CASClient

from opnfv_testapi.common import constants as const
from opnfv_testapi.common.config import CONF
from opnfv_testapi.ui.auth import base


class SigninHandler(base.BaseHandler):
    def get(self):
        client = CASClient(version='2',
                           server_url=CONF.lfid_cas_url,
                           service_url=CONF.ui_url)
        self.redirect(url=(client.get_login_url()))


class SignoutHandler(base.BaseHandler):
    def get(self):
        """Handle signout request."""
        self.clear_cookie(const.TESTAPI_ID)
        client = CASClient(version='2',
                           server_url=CONF.lfid_cas_url)
        self.redirect(url=(client.get_logout_url(redirect_url=CONF.ui_url)))
