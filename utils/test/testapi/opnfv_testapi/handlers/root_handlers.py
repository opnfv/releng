from opnfv_testapi.common.config import CONF
from opnfv_testapi.handlers import base_handlers


class RootHandler(base_handlers.GenericApiHandler):
    def get_template_path(self):
        return CONF.ui_static_path

    def get(self):
        self.render('testapi-ui/index.html')
