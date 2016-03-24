from urllib2 import Request, urlopen, URLError
import json
import jinja2
import os
import re
import requests
import time
import yaml

# Declaration of the variables
functest_test_list = ['vPing', 'vPing_userdata',
                      'Tempest', 'Rally',
                      'ODL', 'ONOS', 'vIMS']
# functest_test_list = ['vPing']
# functest_test_list = []
companion_test_list = ['doctor/doctor-notification', 'promise/promise']
# companion_test_list = []
installers = ["apex", "compass", "fuel", "joid"]
# installers = ["apex"]
PERIOD = 10

# Correspondance between the name of the test case and the name in the DB
# ideally we should modify the DB to avoid such interface....
# '<name in the DB':'<name in the config'>
# I know it is uggly...
test_match_matrix = {'vPing': 'vping_ssh',
                     'vPing_userdata': 'vping_userdata',
                     'ODL': 'odl',
                     'ONOS': 'onos',
                     'Tempest': 'tempest',
                     'Rally': 'rally',
                     'vIMS': 'vims',
                     'doctor-notification': 'doctor',
                     'promise': 'promise'}


class TestCase(object):
    def __init__(self, name, project, criteria=-1, isRunnable=True):
        self.name = name
        self.project = project
        self.criteria = criteria
        self.isRunnable = isRunnable

    def getName(self):
        return self.name

    def getProject(self):
        return self.project

    def getCriteria(self):
        return self.criteria

    def setCriteria(self, criteria):
        self.criteria = criteria

    def setIsRunnable(self, isRunnable):
        self.ssRunnable = isRunnable

    def checkRunnable(self, installer, scenario, config):
        # Re-use Functest declaration
        # Retrieve Functest configuration file functest_config.yaml
        is_runnable = True
        config_test = ""
        TEST_ENV = functest_yaml_config.get("test-dependencies")

        # print " *********************** "
        # print TEST_ENV
        # print " ---------------------- "
        # print "case = " + self.name
        # print "installer = " + installer
        # print "scenario = " + scenario
        # print "project = " + self.project

        # Retrieve test constraints
        case_name_formated = test_match_matrix[self.name]

        try:
            config_test = TEST_ENV[self.project][case_name_formated]
        except KeyError:
            # if not defined in dependencies => no dependencies
            config_test = TEST_ENV[case_name_formated]
        except Exception, e:
            print "Error [getTestEnv]:", e

        # Retrieve test execution param
        test_execution_context = {"installer": installer,
                                  "scenario": scenario}
        # By default we assume that all the tests are always runnable...
        # if test_env not empty => dependencies to be checked
        if config_test is not None and len(config_test) > 0:
            # possible criteria = ["installer", "scenario"]
            # consider test criteria from config file
            # compare towards CI env through CI en variable
            for criteria in config_test:
                if re.search(config_test[criteria],
                             test_execution_context[criteria]) is None:
                    # print "Test "+ test + " cannot be run on the environment"
                    is_runnable = False
        # print is_runnable
        self.isRunnable = is_runnable


def getApiResults(case, installer, scenario):
    case = case.getName()
    results = json.dumps([])
    # to remove proxy (to be removed at the end for local test only)
    # proxy_handler = urllib2.ProxyHandler({})
    # opener = urllib2.build_opener(proxy_handler)
    # urllib2.install_opener(opener)
    # url = "http://127.0.0.1:8000/results?case=" + case + \
    #       "&period=30&installer=" + installer
    url = "http://testresults.opnfv.org/testapi/results?case=" + case + \
          "&period=" + str(PERIOD) + "&installer=" + installer + \
          "&scenario=" + scenario
    request = Request(url)

    try:
        response = urlopen(request)
        k = response.read()
        results = json.loads(k)
    except URLError, e:
        print 'No kittez. Got an error code:', e

    return results


def getScenarios(case, installer):

    case = case.getName()
    url = "http://testresults.opnfv.org/testapi/results?case=" + case + \
          "&period=" + str(PERIOD) + "&installer=" + installer
    request = Request(url)

    try:
        response = urlopen(request)
        k = response.read()
        results = json.loads(k)
    except URLError, e:
        print 'Got an error code:', e

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


def getNbtestOk(results):
    nb_test_ok = 0
    for r in results:
        for k, v in r.iteritems():
            try:
                if "passed" in v:
                    nb_test_ok += 1
            except:
                print "Cannot retrieve test status"
    return nb_test_ok


def getResult(testCase, installer, scenario):

    # retrieve raw results
    results = getApiResults(testCase, installer, scenario)
    # let's concentrate on test results only
    test_results = results['test_results']

    # if results found, analyze them
    if test_results is not None:
        test_results.reverse()

        scenario_results = []

        # print " ---------------- "
        # print test_results
        # print " ---------------- "
        # print "nb of results:" + str(len(test_results))

        for r in test_results:
            # print r["creation_date"]
            # print r["criteria"]
            scenario_results.append({r["creation_date"]: r["criteria"]})
        # sort results
        scenario_results.sort()
        # 4 levels for the results
        # 3: 4+ consecutive runs passing the success criteria
        # 2: <4 successful consecutive runs but passing the criteria
        # 1: close to pass the success criteria
        # 0: 0% success, not passing
        test_result_indicator = 0
        nbTestOk = getNbtestOk(scenario_results)
        # print "Nb test OK:"+ str(nbTestOk)
        # check that we have at least 4 runs
        if nbTestOk < 1:
            test_result_indicator = 0
        elif nbTestOk < 2:
            test_result_indicator = 1
        else:
            # Test the last 4 run
            if (len(scenario_results) > 3):
                last4runResults = scenario_results[-4:]
                if getNbtestOk(last4runResults):
                    test_result_indicator = 3
                else:
                    test_result_indicator = 2
            else:
                test_result_indicator = 2
    print "        >>>> Test indicator:" + str(test_result_indicator)
    return test_result_indicator

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


# init just tempest to get the list of scenarios
# as all the scenarios run Tempest
tempest = TestCase("Tempest", "functest", -1)

# Retrieve the Functest configuration to detect which tests are relevant
# according to the installer, scenario
response = requests.get('https://git.opnfv.org/cgit/functest/plain/testcases/config_functest.yaml')
functest_yaml_config = yaml.load(response.text)

print "****************************************"
print "*   Generating reporting.....          *"
print "****************************************"
# For all the installers
for installer in installers:
    # get scenarios
    scenario_results = getScenarios(tempest, installer)
    scenario_stats = getScenarioStats(scenario_results)

    items = {}
    # For all the scenarios get results
    for s, s_result in scenario_results.items():
        testCases = []
        # For each scenario decalre the test cases
        # Functest cases
        for test_case in functest_test_list:
            testCases.append(TestCase(test_case, "functest"))

        # project/case
        for test_case in companion_test_list:
            test_split = test_case.split("/")
            test_project = test_split[0]
            test_case = test_split[1]
            testCases.append(TestCase(test_case, test_project))

        # Check if test case is runnable according to the installer, scenario
        for test_case in testCases:
            test_case.checkRunnable(installer, s, functest_yaml_config)
            # print "testcase %s is %s" % (test_case.getName(),
            #                              test_case.isRunnable)

        print "--------------------------"
        print "%s / %s:" % (installer, s)
        for testCase in testCases:
            time.sleep(1)
            if testCase.isRunnable:
                print "    Searching results for case %s " % testCase.getName()
                result = getResult(testCase, installer, s)
                testCase.setCriteria(result)
                items[s] = testCases
        print "--------------------------"
    print "****************************************"
    templateLoader = jinja2.FileSystemLoader(os.path.dirname(os.path.abspath(__file__)))
    templateEnv = jinja2.Environment(loader=templateLoader)

    TEMPLATE_FILE = "index-status-tmpl.html"
    template = templateEnv.get_template(TEMPLATE_FILE)

    outputText = template.render(scenario_stats=scenario_stats,
                                 items=items,
                                 installer=installer,
                                 period=PERIOD)

    with open("index-status-" + installer + ".html", "wb") as fh:
        fh.write(outputText)
