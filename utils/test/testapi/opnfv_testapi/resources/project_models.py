##############################################################################
# Copyright (c) 2015 Orange
# guyrodrigue.koffi@orange.com / koffirodrigue@gmail.com
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
from opnfv_testapi.resources import models
from opnfv_testapi.tornado_swagger import swagger


@swagger.model()
class ProjectCreateRequest(models.ModelBase):
    def __init__(self, name, description=''):
        self.name = name
        self.description = description


@swagger.model()
class ProjectUpdateRequest(models.ModelBase):
    def __init__(self, name='', description=''):
        self.name = name
        self.description = description


@swagger.model()
class Project(models.ModelBase):
    def __init__(self,
                 name=None, _id=None, description=None, create_date=None):
        self._id = _id
        self.name = name
        self.description = description
        self.creation_date = create_date


@swagger.model()
class Projects(models.ModelBase):
    """
        @property projects:
        @ptype projects: C{list} of L{Project}
    """
    def __init__(self):
        self.projects = list()

    @staticmethod
    def attr_parser():
        return {'projects': Project}
