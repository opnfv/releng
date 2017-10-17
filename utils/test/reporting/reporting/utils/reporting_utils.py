#!/usr/bin/python
#
# This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
import logging
import json
import os
import requests
import pdfkit
import yaml

from urllib2 import Request, urlopen, URLError


# ----------------------------------------------------------
#
#               YAML UTILS
#
# -----------------------------------------------------------
def get_parameter_from_yaml(parameter, config_file):
    """
    Returns the value of a given parameter in file.yaml
    parameter must be given in string format with dots
    Example: general.openstack.image_name
    """
    with open(config_file) as my_file:
        file_yaml = yaml.safe_load(my_file)
    my_file.close()
    value = file_yaml
    for element in parameter.split("."):
        value = value.get(element)
        if value is None:
            raise ValueError("The parameter %s is not defined in"
                             " reporting.yaml" % parameter)
    return value


def get_config(parameter):
    """
    Get configuration parameter from yaml configuration file
    """
    yaml_ = os.environ["CONFIG_REPORTING_YAML"]
    return get_parameter_from_yaml(parameter, yaml_)


# ----------------------------------------------------------
#
#               LOGGER UTILS
#
# -----------------------------------------------------------
def getLogger(module):
    """
    Get Logger
    """
    log_formatter = logging.Formatter("%(asctime)s [" +
                                      module +
                                      "] [%(levelname)-5.5s]  %(message)s")
    logger = logging.getLogger()
    log_file = get_config('general.log.log_file')
    log_level = get_config('general.log.log_level')

    file_handler = logging.FileHandler("{0}/{1}".format('.', log_file))
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)
    logger.setLevel(log_level)
    return logger


# ----------------------------------------------------------
#
#               REPORTING UTILS
#
# -----------------------------------------------------------
def getApiResults(case, installer, scenario, version):
    """
    Get Results by calling the API
    """
    results = json.dumps([])
    # to remove proxy (to be removed at the end for local test only)
    # proxy_handler = urllib2.ProxyHandler({})
    # opener = urllib2.build_opener(proxy_handler)
    # urllib2.install_opener(opener)
    # url = "http://127.0.0.1:8000/results?case=" + case + \
    #       "&period=30&installer=" + installer
    period = get_config('general.period')
    url_base = get_config('testapi.url')
    nb_tests = get_config('general.nb_iteration_tests_success_criteria')

    url = ("http://" + url_base + "?case=" + case +
           "&period=" + str(period) + "&installer=" + installer +
           "&scenario=" + scenario + "&version=" + version +
           "&last=" + str(nb_tests))
    request = Request(url)

    try:
        response = urlopen(request)
        k = response.read()
        results = json.loads(k)
    except URLError:
        print "Error when retrieving results form API"

    return results


def getScenarios(project, case, installer, version):
    """
    Get the list of Scenarios
    """

    period = get_config('general.period')
    url_base = get_config('testapi.url')

    url = ("http://" + url_base +
           "?installer=" + installer +
           "&period=" + str(period))

    if version is not None:
        url += "&version=" + version

    if project is not None:
        url += "&project=" + project

    if case is not None:
        url += "&case=" + case

    try:
        request = Request(url)
        response = urlopen(request)
        k = response.read()
        results = json.loads(k)
        test_results = results['results']
        try:
            page = results['pagination']['total_pages']
            if page > 1:
                test_results = []
                for i in range(1, page + 1):
                    url_page = url + "&page=" + str(i)
                    request = Request(url_page)
                    response = urlopen(request)
                    k = response.read()
                    results = json.loads(k)
                    test_results += results['results']
        except KeyError:
            print "No pagination detected"
    except URLError as err:
        print 'Got an error code: {}'.format(err)

    if test_results is not None:
        test_results.reverse()
        scenario_results = {}

        for my_result in test_results:
            # Retrieve all the scenarios per installer
            if not my_result['scenario'] in scenario_results.keys():
                scenario_results[my_result['scenario']] = []
            # Do we consider results from virtual pods ...
            # Do we consider results for non HA scenarios...
            exclude_virtual_pod = get_config('functest.exclude_virtual')
            exclude_noha = get_config('functest.exclude_noha')
            if ((exclude_virtual_pod and "virtual" in my_result['pod_name']) or
                    (exclude_noha and "noha" in my_result['scenario'])):
                print "exclude virtual pod results..."
            else:
                scenario_results[my_result['scenario']].append(my_result)

    return scenario_results


def getScenarioStats(scenario_results):
    """
    Get the number of occurence of scenarios over the defined PERIOD
    """
    scenario_stats = {}
    for res_k, res_v in scenario_results.iteritems():
        scenario_stats[res_k] = len(res_v)
    return scenario_stats


def getScenarioStatus(installer, version):
    """
    Get the status of a scenariofor Yardstick
    """
    period = get_config('general.period')
    url_base = get_config('testapi.url')

    url = ("http://" + url_base + "?case=scenario_status" +
           "&installer=" + installer +
           "&version=" + version + "&period=" + str(period))
    request = Request(url)

    try:
        response = urlopen(request)
        k = response.read()
        response.close()
        results = json.loads(k)
        test_results = results['results']
    except URLError:
        print "GetScenarioStatus: error when calling the API"

    x86 = 'x86'
    aarch64 = 'aarch64'
    scenario_results = {x86: {}, aarch64: {}}
    result_dict = {x86: {}, aarch64: {}}
    if test_results is not None:
        for test_r in test_results:
            if (test_r['stop_date'] != 'None' and
                    test_r['criteria'] is not None):
                scenario_name = test_r['scenario']
                if 'arm' in test_r['pod_name']:
                    if not test_r['scenario'] in scenario_results[aarch64]:
                        scenario_results[aarch64][scenario_name] = []
                    scenario_results[aarch64][scenario_name].append(test_r)
                else:
                    if not test_r['scenario'] in scenario_results[x86]:
                        scenario_results[x86][scenario_name] = []
                    scenario_results[x86][scenario_name].append(test_r)

        for key in scenario_results:
            for scen_k, scen_v in scenario_results[key].items():
                # scenario_results[k] = v[:LASTEST_TESTS]
                s_list = []
                for element in scen_v:
                    if element['criteria'] == 'PASS':
                        s_list.append(1)
                    else:
                        s_list.append(0)
                result_dict[key][scen_k] = s_list

    # return scenario_results
    return result_dict


def getQtipResults(version, installer):
    """
    Get QTIP results
    """
    period = get_config('qtip.period')
    url_base = get_config('testapi.url')

    url = ("http://" + url_base + "?project=qtip" +
           "&installer=" + installer +
           "&version=" + version + "&period=" + str(period))
    request = Request(url)

    try:
        response = urlopen(request)
        k = response.read()
        response.close()
        results = json.loads(k)['results']
    except URLError as err:
        print 'Got an error code: {}'.format(err)

    result_dict = {}
    if results:
        for r in results:
            key = '{}/{}'.format(r['pod_name'], r['scenario'])
            if key not in result_dict.keys():
                result_dict[key] = []
            result_dict[key].append(r['details']['score'])

    # return scenario_results
    return result_dict


def getNbtestOk(results):
    """
    based on default value (PASS) count the number of test OK
    """
    nb_test_ok = 0
    for my_result in results:
        for res_k, res_v in my_result.iteritems():
            try:
                if "PASS" in res_v:
                    nb_test_ok += 1
            except Exception:
                print "Cannot retrieve test status"
    return nb_test_ok


def getCaseScore(testCase, installer, scenario, version):
    """
    Get Result  for a given Functest Testcase
    """
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

        for res_r in test_results:
            # print r["start_date"]
            # print r["criteria"]
            scenario_results.append({res_r["start_date"]: res_r["criteria"]})
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
            if len(scenario_results) > 3:
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


def getCaseScoreFromBuildTag(testCase, s_results):
    """
    Get Results for a given Functest Testcase with arch filtering
    """
    url_base = get_config('testapi.url')
    nb_tests = get_config('general.nb_iteration_tests_success_criteria')
    test_result_indicator = 0
    # architecture is not a result field...so we cannot use getResult as it is
    res_matrix = []
    try:
        for s_result in s_results:
            build_tag = s_result['build_tag']
            d = s_result['start_date']
            res_matrix.append({'date': d,
                               'build_tag': build_tag})
        # sort res_matrix
        filter_res_matrix = sorted(res_matrix, key=lambda k: k['date'],
                                   reverse=True)[:nb_tests]
        for my_res in filter_res_matrix:
            url = ("http://" + url_base + "?case=" + testCase +
                   "&build_tag=" + my_res['build_tag'])
            request = Request(url)
            response = urlopen(request)
            k = response.read()
            results = json.loads(k)
            if "PASS" in results['results'][0]['criteria']:
                test_result_indicator += 1
    except:
        print "No results found for this case"
    if test_result_indicator > 3:
        test_result_indicator = 3

    return test_result_indicator


def getJenkinsUrl(build_tag):
    """
    Get Jenkins url_base corespoding to the last test CI run
    e.g. jenkins-functest-apex-apex-daily-colorado-daily-colorado-246
    id = 246
    jenkins-functest-compass-huawei-pod5-daily-master-136
    id = 136
    note it is linked to jenkins format
    if this format changes...function to be adapted....
    """
    url_base = get_config('functest.jenkins_url')
    try:
        build_id = [int(s) for s in build_tag.split("-") if s.isdigit()]
        url_id = (build_tag[8:-(len(str(build_id[0])) + 1)] +
                  "/" + str(build_id[0]))
        jenkins_url = url_base + url_id + "/console"
    except Exception:
        print 'Impossible to get jenkins url:'

    if "jenkins-" not in build_tag:
        jenkins_url = None

    return jenkins_url


def getScenarioPercent(scenario_score, scenario_criteria):
    """
    Get success rate of the scenario (in %)
    """
    score = 0.0
    try:
        score = float(scenario_score) / float(scenario_criteria) * 100
    except Exception:
        print 'Impossible to calculate the percentage score'
    return score


# *********
# Functest
# *********
def getFunctestConfig(version=""):
    """
    Get Functest configuration
    """
    config_file = get_config('functest.test_conf') + version
    response = requests.get(config_file)
    return yaml.safe_load(response.text)


def getArchitectures(scenario_results):
    """
    Get software architecture (x86 or Aarch64)
    """
    supported_arch = ['x86']
    if len(scenario_results) > 0:
        for scenario_result in scenario_results.values():
            for value in scenario_result:
                if "armband" in value['build_tag']:
                    supported_arch.append('aarch64')
                    return supported_arch
    return supported_arch


def filterArchitecture(results, architecture):
    """
    Restrict the list of results based on given architecture
    """
    filtered_results = {}
    for name, res in results.items():
        filtered_values = []
        for value in res:
            if architecture is "x86":
                # drop aarch64 results
                if ("armband" not in value['build_tag']):
                    filtered_values.append(value)
            elif architecture is "aarch64":
                # drop x86 results
                if ("armband" in value['build_tag']):
                    filtered_values.append(value)
        if (len(filtered_values) > 0):
            filtered_results[name] = filtered_values
    return filtered_results


# *********
# Yardstick
# *********
def subfind(given_list, pattern_list):
    """
    Yardstick util function
    """
    LASTEST_TESTS = get_config('general.nb_iteration_tests_success_criteria')
    for i in range(len(given_list)):
        if given_list[i] == pattern_list[0] and \
                given_list[i:i + LASTEST_TESTS] == pattern_list:
            return True
    return False


def _get_percent(status):
    """
    Yardstick util function to calculate success rate
    """
    if status * 100 % 6:
        return round(float(status) * 100 / 6, 1)
    else:
        return status * 100 / 6


def get_percent(four_list, ten_list):
    """
    Yardstick util function to calculate success rate
    """
    four_score = 0
    ten_score = 0

    for res_v in four_list:
        four_score += res_v
    for res_v in ten_list:
        ten_score += res_v

    LASTEST_TESTS = get_config('general.nb_iteration_tests_success_criteria')
    if four_score == LASTEST_TESTS:
        status = 6
    elif subfind(ten_list, [1, 1, 1, 1]):
        status = 5
    elif ten_score == 0:
        status = 0
    else:
        status = four_score + 1

    return _get_percent(status)


def _test():
    """
    Yardstick util function (test)
    """
    status = getScenarioStatus("compass", "master")
    print "status:++++++++++++++++++++++++"
    print json.dumps(status, indent=4)


# ----------------------------------------------------------
#
#               Export
#
# -----------------------------------------------------------

def export_csv(scenario_file_name, installer, version):
    """
    Generate sub files based on scenario_history.txt
    """
    scenario_installer_file_name = ("./display/" + version +
                                    "/functest/scenario_history_" +
                                    installer + ".csv")
    scenario_installer_file = open(scenario_installer_file_name, "a")
    with open(scenario_file_name, "r") as scenario_file:
        scenario_installer_file.write("date,scenario,installer,detail,score\n")
        for line in scenario_file:
            if installer in line:
                scenario_installer_file.write(line)
    scenario_installer_file.close


def generate_csv(scenario_file):
    """
    Generate sub files based on scenario_history.txt
    """
    import shutil
    csv_file = scenario_file.replace('txt', 'csv')
    shutil.copy2(scenario_file, csv_file)


def export_pdf(pdf_path, pdf_doc_name):
    """
    Export results to pdf
    """
    try:
        pdfkit.from_file(pdf_path, pdf_doc_name)
    except IOError:
        print "Error but pdf generated anyway..."
    except Exception:
        print "impossible to generate PDF"
