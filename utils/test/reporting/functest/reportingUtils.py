#!/usr/bin/python
#
# This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
from urllib2 import Request, urlopen, URLError
import json
import reportingConf


def getApiResults(case, installer, scenario, version):
    results = json.dumps([])
    # to remove proxy (to be removed at the end for local test only)
    # proxy_handler = urllib2.ProxyHandler({})
    # opener = urllib2.build_opener(proxy_handler)
    # urllib2.install_opener(opener)
    # url = "http://127.0.0.1:8000/results?case=" + case + \
    #       "&period=30&installer=" + installer
    url = (reportingConf.URL_BASE + "?case=" + case +
           "&period=" + str(reportingConf.PERIOD) + "&installer=" + installer +
           "&scenario=" + scenario + "&version=" + version +
           "&last=" + str(reportingConf.NB_TESTS))
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
    print case
    url = (reportingConf.URL_BASE + "?case=" + case +
           "&period=" + str(reportingConf.PERIOD) + "&installer=" + installer +
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
        test_result_indicator = 0
        nbTestOk = getNbtestOk(scenario_results)
        # print "Nb test OK (last 10 days):"+ str(nbTestOk)
        # check that we have at least 4 runs
        if nbTestOk < 1:
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
