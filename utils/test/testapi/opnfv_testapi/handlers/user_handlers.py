from opnfv_testapi.common import constants
from opnfv_testapi.common import raises
from opnfv_testapi.common.config import CONF
from opnfv_testapi.handlers import base_handlers
from opnfv_testapi.models.user_models import User


class UserHandler(base_handlers.GenericApiHandler):
    def __init__(self, application, request, **kwargs):
        super(UserHandler, self).__init__(application, request, **kwargs)
        self.table = 'users'
        self.table_cls = User

    def get(self):
        if CONF.api_authenticate:
            username = self.get_secure_cookie(constants.TESTAPI_ID)
            if username:
                self._get_one(query={'user': username})
            else:
                raises.Unauthorized('Unauthorized')
        else:
            self.finish_request(User('anonymous',
                                     'anonymous@linuxfoundation.com',
                                     'anonymous lf',
                                     constants.TESTAPI_USERS).format())
