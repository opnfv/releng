from opnfv_testapi.common import check
from opnfv_testapi.common.config import CONF
from opnfv_testapi.resources import handlers


class RootHandler(handlers.GenericApiHandler):
    def get_template_path(self):
        return CONF.ui_static_path

    @check.login
    def get(self):
        self.render('testapi-ui/index.html')
