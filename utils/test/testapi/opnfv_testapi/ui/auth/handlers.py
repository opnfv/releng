from six.moves.urllib import parse

from opnfv_testapi.common import config
from opnfv_testapi.resources import handlers
from opnfv_testapi.ui.auth import constants as const
from opnfv_testapi.ui.auth import utils


CONF = config.Config()


class SigninHandler(handlers.GenericApiHandler):
    def get(self):
        csrf_token = utils.get_token()
        return_endpoint = parse.urljoin(CONF.api_url,
                                        CONF.osid_openid_return_to)
        return_to = utils.set_query_params(return_endpoint,
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
        url = utils.set_query_params(url, params)
        self.redirect(url=url, permanent=False)


class SigninReturnHandler(handlers.GenericApiHandler):
    def get(self):
        self.redirect(url=CONF.ui_url)
