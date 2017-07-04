#!/usr/bin/python
#
# This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
#
# http://www.apache.org/licenses/LICENSE-2.0
#


class ScenarioResult(object):

    def __init__(self, status, score=0, score_percent=0, url_lastrun=''):
        self.status = status
        self.score = score
        self.score_percent = score_percent
        self.url_lastrun = url_lastrun

    def getStatus(self):
        return self.status

    def getScore(self):
        return self.score

    def getScorePercent(self):
        return self.score_percent

    def getUrlLastRun(self):
        return self.url_lastrun
