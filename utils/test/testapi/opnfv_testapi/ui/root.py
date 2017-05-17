from opnfv_testapi.resources.handlers import GenericApiHandler
from opnfv_testapi.common import config


class RootHandler(GenericApiHandler):
    def get_template_path(self):
        return config.Config().static_path

    def get(self):
        self.render('testapi-ui/index.html')
