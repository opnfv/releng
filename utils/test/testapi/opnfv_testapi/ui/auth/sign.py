from six.moves.urllib import parse

from opnfv_testapi.common import config
from opnfv_testapi.ui.auth import base
from opnfv_testapi.ui.auth import constants as const

CONF = config.Config()


class SigninHandler(base.BaseHandler):
    def get(self):
        csrf_token = base.get_token()
        return_endpoint = parse.urljoin(CONF.api_url,
                                        CONF.osid_openid_return_to)
        return_to = base.set_query_params(return_endpoint,
                                          {const.CSRF_TOKEN: csrf_token})

        params = {
            const.OPENID_MODE: CONF.osid_openid_mode,
            const.OPENID_NS: CONF.osid_openid_ns,
            const.OPENID_RETURN_TO: return_to,
            const.OPENID_CLAIMED_ID: CONF.osid_openid_claimed_id,
            const.OPENID_IDENTITY: CONF.osid_openid_identity,
            const.OPENID_REALM: CONF.api_url,
            const.OPENID_NS_SREG: CONF.osid_openid_ns_sreg,
            const.OPENID_NS_SREG_REQUIRED: CONF.osid_openid_sreg_required,
        }
        url = CONF.osid_openstack_openid_endpoint
        url = base.set_query_params(url, params)
        self.redirect(url=url, permanent=False)


class SigninReturnHandler(base.BaseHandler):
    def get(self):
        if self.get_query_argument(const.OPENID_MODE) == 'cancel':
            self._auth_failure('Authentication canceled.')

        openid = self.get_query_argument(const.OPENID_CLAIMED_ID)
        user_info = {
            'openid': openid,
            'email': self.get_query_argument(const.OPENID_NS_SREG_EMAIL),
            'fullname': self.get_query_argument(const.OPENID_NS_SREG_FULLNAME)
        }

        self.db_save(self.table, user_info)
        if not self.get_secure_cookie('openid'):
            self.set_secure_cookie('openid', openid)
        self.redirect(url=CONF.ui_url)
        
        
    def _auth_failure(self, message):
        params = {
            'message': message
        }
        url = parse.urljoin(CONF.ui_url,
                            '/#/auth_failure?' + parse.urlencode(params))
        self.redirect(url)

