#!/usr/bin/python
#
# This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
from urllib2 import Request, urlopen, URLError
import logging
import json
import reportingConf as conf


def getLogger(module):
    logFormatter = logging.Formatter("%(asctime)s [" +
                                     module +
                                     "] [%(levelname)-5.5s]  %(message)s")
    logger = logging.getLogger()

    fileHandler = logging.FileHandler("{0}/{1}".format('.', conf.LOG_FILE))
    fileHandler.setFormatter(logFormatter)
    logger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
    logger.setLevel(conf.LOG_LEVEL)
    return logger


def getScenarioStatus(installer, version):
    url = (conf.URL_BASE + "?case=" + "scenario_status" +
           "&installer=" + installer +
           "&version=" + version +"&period=" + str(conf.PERIOD))
    request = Request(url)

    try:
        response = urlopen(request)
        k = response.read()
        response.close()
        results = json.loads(k)
        test_results = results['results']
    except URLError, e:
        print 'Got an error code:', e

    scenario_results = {}
    result_dict = {}
    if test_results is not None:
        for r in test_results:
            if r['stop_date'] != 'None' and r['criteria'] is not None:
                if not r['scenario'] in scenario_results.keys():
                    scenario_results[r['scenario']] = []
                scenario_results[r['scenario']].append(r)

        for k,v in scenario_results.items():
            # scenario_results[k] = v[:conf.LASTEST_TESTS]
            s_list = []
            for element in v:
                if element['criteria'] == 'SUCCESS':
                    s_list.append(1)
                else:
                    s_list.append(0)
            result_dict[k] = s_list

    # return scenario_results
    return result_dict

def subfind(given_list, pattern_list):
    for i in range(len(given_list)):
        if given_list[i] == pattern_list[0] and given_list[i:i + conf.LASTEST_TESTS] == pattern_list:
            return True
    return False

def get_percent(status):
    
    if status * 100 % 6:
        return round(float(status) * 100 / 6, 1)
    else:
        return status * 100 / 6

def get_status(four_list, ten_list):
    four_score = 0
    ten_score = 0

    for v in four_list:
        four_score += v
    for v in ten_list:
        ten_score += v

    if four_score == conf.LASTEST_TESTS:
        status = 6
    elif subfind(ten_list, [1, 1, 1, 1]):
        status = 5
    elif ten_score == 0:
        status = 0
    else:
        status = four_score + 1

    return get_percent(status)


def _test():
    status = getScenarioStatus("compass", "master")
    print "status:++++++++++++++++++++++++"
    print json.dumps(status,indent=4)


if __name__ == '__main__':    # pragma: no cover
    _test()
