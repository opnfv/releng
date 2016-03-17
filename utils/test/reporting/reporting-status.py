from urllib2 import Request, urlopen, URLError
import urllib2
import json
import jinja2
import os
import random


class TestCase(object):
    def __init__(self, name, project, criteria=-1):
        self.name = name
        self.project = project
        self.criteria = criteria

    def getName(self):
        return self.name

    def getProject(self):
        return self.project

    def getCriteria(self):
        return self.criteria

    def setCriteria(self, criteria):
        self.criteria = criteria


def getApiResults(case, installer):
    case = case.getName()

    # to remove proxy (to be removed at the end for local test only)
    # proxy_handler = urllib2.ProxyHandler({})
    # opener = urllib2.build_opener(proxy_handler)
    # urllib2.install_opener(opener)
    url = "http://testresults.opnfv.org/testapi/results?case=" + case + "&period=30&installer=" + installer
    #url = "http://127.0.0.1:8000/results?case=" + case + "&period=30&installer=" + installer
    request = Request(url)

    try:
        response = urlopen(request)
        k = response.read()
        results = json.loads(k)
    except URLError, e:
        print 'No kittez. Got an error code:', e

    return results


def getScenarios(case, installer):

    results = getApiResults(case, installer)
    test_results = results['test_results']

    if test_results is not None:
        test_results.reverse()

        scenario_results = {}

        for r in test_results:
            # Retrieve all the scenarios per installer
            if not r['version'] in scenario_results.keys():
                scenario_results[r['version']] = []
            scenario_results[r['version']].append(r)

    return scenario_results


def getScenarioStats(scenario_results):
    scenario_stats = {}
    for k, v in scenario_results.iteritems():
        scenario_stats[k] = len(v)

    return scenario_stats


def getResult(testCase, installer):

    # retrieve raw results
    results = getApiResults(testCase, installer)
    # let's concentrate on test results only
    test_results = results['test_results']

    # if results found, analyze them
    if test_results is not None:
        test_results.reverse()

        scenario_results = {}

        for r in test_results:
            if not r['version'] in scenario_results.keys():
                scenario_results[r['version']] = []
            scenario_results[r['version']].append(r)

        for s, s_result in scenario_results.items():
            scenario_results[s] = s_result[0:5]
            # For each scenario, we build a result object to deal with
            # results, criteria and error handling
            for result in scenario_results[s]:
                result["creation_date"] = result["creation_date"].split(".")[0]

                # Cannot be fully generic
                # need to look for specific criteria case by case
                # TODO add a criteria passed/failed in DB??
                # TODO result["Success_criteria"] = result["success_criteria"]
                # meanwhile just random....
                # and consider the last random arbitrarily
                # 4 levels for the results
                # 3: 4+ consecutive runs passing the success criteria
                # 2: <4 successful consecutive runs but passing the criteria
                # 1: close to pass the success criteria
                # 0: 0% success, not passing
                #

    return int(random.random()*4)+1

# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************

# as the criteria are all difference, we shall use a common way to indicate
# the criteria
# 100 = 100% = all the test must be OK
# 90 = 90% = all the test must be above 90% of success rate
# TODO harmonize success criteria
# some criteria could be the duration, the success rate, the packet loss,...
# to be done case by case
# TODo create TestCriteria Object


installers = ["apex", "compass", "fuel", "joid"]
# init just tempest to get the scenario as all the scenarios run Temepst
tempest = TestCase("Tempest", "functest", -1)

for installer in installers:

    scenario_results = getScenarios(tempest, installer)
    scenario_stats = getScenarioStats(scenario_results)

    items = {}

    for s, s_result in scenario_results.items():

        vPing = TestCase("vPing", "functest")
        vPing_userdata = TestCase("vPing_userdata", "functest")
        tempest = TestCase("Tempest", "functest")
        rally = TestCase("Rally", "functest")
        odl = TestCase("ODL", "functest")
        onos = TestCase("ONOS", "functest")
        ovno = TestCase("OVNO", "functest")
        vIMS = TestCase("vIMS", "functest")
        doctor = TestCase("doctor-notification", "doctor")
        promise = TestCase("promise", "promise")
        odl_vpn = TestCase("ODL VPN Service tests", "sdnvpn")
        bgpvpn_api = TestCase("OpenStack Neutron BGPVPN API extension tests",
                              "sdnvpn")
        testCases = [vPing, vPing_userdata, tempest, rally, odl, onos, vIMS,
                     doctor, promise]

        for testCase in testCases:
            result = getResult(testCase, installer)
            testCase.setCriteria(result)
            # print "case %s (%s) = %s " % (testCase.getName(), s, result)
        items[s] = testCases

    templateLoader = jinja2.FileSystemLoader(os.path.dirname(os.path.abspath(__file__)))
    templateEnv = jinja2.Environment(loader=templateLoader)

    TEMPLATE_FILE = "index-status-tmpl.html"
    template = templateEnv.get_template(TEMPLATE_FILE)

    outputText = template.render(scenario_stats=scenario_stats,
                                 items=items,
                                 installer=installer)

    with open("index-status-" + installer + ".html", "wb") as fh:
        fh.write(outputText)
