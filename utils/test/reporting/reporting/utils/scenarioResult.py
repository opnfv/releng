#!/usr/bin/python
#
# This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
#
# http://www.apache.org/licenses/LICENSE-2.0
#


class ScenarioResult(object):
    def __init__(self, status, four_days_score='', ten_days_score='',
                 score_percent=0.0, last_url=''):
        self.status = status
        self.four_days_score = four_days_score
        self.ten_days_score = ten_days_score
        self.score_percent = score_percent
        self.last_url = last_url

    def getStatus(self):
        return self.status

    def getTenDaysScore(self):
        return self.ten_days_score

    def getFourDaysScore(self):
        return self.four_days_score

    def getScorePercent(self):
        return self.score_percent

    def getLastUrl(self):
        return self.last_url
