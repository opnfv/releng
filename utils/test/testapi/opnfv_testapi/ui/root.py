from opnfv_testapi.resources.handlers import GenericApiHandler
from opnfv_testapi.common.config import CONF


class RootHandler(GenericApiHandler):
    def get_template_path(self):
        return CONF.static_path

    def get(self):
        self.render('testapi-ui/index.html')
