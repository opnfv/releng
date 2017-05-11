from opnfv_testapi.resources.handlers import GenericApiHandler
from opnfv_testapi.tornado_swagger import settings


class UIHandler(GenericApiHandler):
    def initialize(self, **kwargs):
        self.static_path = settings.docs_settings.get('static_path')
        self.base_url = 'http://localhost:8000'

    def get_template_path(self):
        return self.static_path

    def get(self):
        self.render('testapi-ui/index.html')
