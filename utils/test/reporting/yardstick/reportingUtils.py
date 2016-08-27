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
    if test_results is not None:
        for r in test_results:
            if r['stop_date'] != 'None':
                if not r['scenario'] in scenario_results.keys():
                    scenario_results[r['scenario']] = []
                scenario_results[r['scenario']].append(r)

        for k,v in scenario_results.items():
            scenario_results[k] = v[:conf.LASTEST_TESTS]

    return scenario_results


def _test():
    status = getScenarioStatus("compass", "master")
    print "status:++++++++++++++++++++++++"
    print json.dumps(status,indent=4)


if __name__ == '__main__':    # pragma: no cover
    _test()
