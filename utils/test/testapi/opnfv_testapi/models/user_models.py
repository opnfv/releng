from opnfv_testapi.models import base_models


class User(base_models.ModelBase):
    def __init__(self, user=None, email=None, fullname=None, groups=None):
        self.user = user
        self.email = email
        self.fullname = fullname
        self.groups = groups
