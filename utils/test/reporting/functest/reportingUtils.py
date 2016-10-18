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


def getApiResults(case, installer, scenario, version):
    results = json.dumps([])
    # to remove proxy (to be removed at the end for local test only)
    # proxy_handler = urllib2.ProxyHandler({})
    # opener = urllib2.build_opener(proxy_handler)
    # urllib2.install_opener(opener)
    # url = "http://127.0.0.1:8000/results?case=" + case + \
    #       "&period=30&installer=" + installer
    url = ("http://" + conf.URL_BASE + "?case=" + case +
           "&period=" + str(conf.PERIOD) + "&installer=" + installer +
           "&scenario=" + scenario + "&version=" + version +
           "&last=" + str(conf.NB_TESTS))
    request = Request(url)

    try:
        response = urlopen(request)
        k = response.read()
        results = json.loads(k)
    except URLError, e:
        print 'No kittez. Got an error code:', e

    return results


def getScenarios(case, installer, version):

    case = case.getName()
    url = ("http://" + conf.URL_BASE + "?case=" + case +
           "&period=" + str(conf.PERIOD) + "&installer=" + installer +
           "&version=" + version)
    request = Request(url)

    try:
        response = urlopen(request)
        k = response.read()
        results = json.loads(k)
        test_results = results['results']
    except URLError, e:
        print 'Got an error code:', e

    if test_results is not None:
        test_results.reverse()

        scenario_results = {}

        for r in test_results:
            # Retrieve all the scenarios per installer
            if not r['scenario'] in scenario_results.keys():
                scenario_results[r['scenario']] = []
            scenario_results[r['scenario']].append(r)

    return scenario_results


def getScenarioStats(scenario_results):
    scenario_stats = {}
    for k, v in scenario_results.iteritems():
        scenario_stats[k] = len(v)

    return scenario_stats


def getNbtestOk(results):
    nb_test_ok = 0
    for r in results:
        for k, v in r.iteritems():
            try:
                if "PASS" in v:
                    nb_test_ok += 1
            except:
                print "Cannot retrieve test status"
    return nb_test_ok


def getResult(testCase, installer, scenario, version):

    # retrieve raw results
    results = getApiResults(testCase, installer, scenario, version)
    # let's concentrate on test results only
    test_results = results['results']

    # if results found, analyze them
    if test_results is not None:
        test_results.reverse()

        scenario_results = []

        # print " ---------------- "
        # print test_results
        # print " ---------------- "
        # print "nb of results:" + str(len(test_results))

        for r in test_results:
            # print r["start_date"]
            # print r["criteria"]
            scenario_results.append({r["start_date"]: r["criteria"]})
        # sort results
        scenario_results.sort()
        # 4 levels for the results
        # 3: 4+ consecutive runs passing the success criteria
        # 2: <4 successful consecutive runs but passing the criteria
        # 1: close to pass the success criteria
        # 0: 0% success, not passing
        # -1: no run available
        test_result_indicator = 0
        nbTestOk = getNbtestOk(scenario_results)

        # print "Nb test OK (last 10 days):"+ str(nbTestOk)
        # check that we have at least 4 runs
        if len(scenario_results) < 1:
            # No results available
            test_result_indicator = -1
        elif nbTestOk < 1:
            test_result_indicator = 0
        elif nbTestOk < 2:
            test_result_indicator = 1
        else:
            # Test the last 4 run
            if (len(scenario_results) > 3):
                last4runResults = scenario_results[-4:]
                nbTestOkLast4 = getNbtestOk(last4runResults)
                # print "Nb test OK (last 4 run):"+ str(nbTestOkLast4)
                if nbTestOkLast4 > 3:
                    test_result_indicator = 3
                else:
                    test_result_indicator = 2
            else:
                test_result_indicator = 2
    return test_result_indicator


def getJenkinsUrl(build_tag):
    # e.g. jenkins-functest-apex-apex-daily-colorado-daily-colorado-246
    # id = 246
    # note it is linked to jenkins format
    # if this format changes...function to be adapted....
    url_base = "https://build.opnfv.org/ci/view/functest/job/"
    jenkins_url = ""
    try:
        build_id = [int(s) for s in build_tag.split("-") if s.isdigit()]
        jenkins_path = filter(lambda c: not c.isdigit(), build_tag)
        url_id = jenkins_path[8:-1] + "/" + str(build_id[0])
        jenkins_url = url_base + url_id + "/console"
    except:
        print 'Impossible to get jenkins url:'

    return jenkins_url

def getScenarioPercent(scenario_score,scenario_criteria):
    score = 0.0
    try:
        score = float(scenario_score) / float(scenario_criteria) * 100
    except:
        print 'Impossible to calculate the percentage score'
    return score
