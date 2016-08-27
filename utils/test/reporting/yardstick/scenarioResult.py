#!/usr/bin/python
#
# This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
#
# http://www.apache.org/licenses/LICENSE-2.0
#


class ScenarioResult(object):
    def __init__(self, status, score=0):
        self.status = status
        self.score = score

    def getStatus(self):
        return self.status

    def getScore(self):
        return self.score
