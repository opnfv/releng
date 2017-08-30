from opnfv_testapi.common import check
from opnfv_testapi.common.config import CONF
from opnfv_testapi.resources.handlers import GenericApiHandler


class RootHandler(GenericApiHandler):
    def get_template_path(self):
        return CONF.static_path

    @check.login
    def get(self):
        self.render('testapi-ui/index.html')
