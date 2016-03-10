from urllib2 import Request, urlopen, URLError
import json
import jinja2
import os

installers = ["apex", "compass", "fuel", "joid"]
items = ["tests", "Success rate", "duration"]

for installer in installers:
    # we consider the Tempest results of the last 7 days
    url = "http://testresults.opnfv.org/testapi/results?case=Tempest"
    request = Request(url + '&period=7&installer=' + installer)

    try:
        response = urlopen(request)
        k = response.read()
        results = json.loads(k)
    except URLError, e:
        print 'No kittez. Got an error code:', e

    test_results = results['test_results']
    test_results.reverse()

    scenario_results = {}
    criteria = {}
    errors = {}

    for r in test_results:
        # Retrieve all the scenarios per installer
        if not r['version'] in scenario_results.keys():
            scenario_results[r['version']] = []
        scenario_results[r['version']].append(r)

    for s, s_result in scenario_results.items():
        scenario_results[s] = s_result[0:5]
        # For each scenario, we build a result object to deal with
        # results, criteria and error handling
        for result in scenario_results[s]:
            result["creation_date"] = result["creation_date"].split(".")[0]

            # retrieve results
            # ****************
            nb_tests_run = result['details']['tests']
            if nb_tests_run != 0:
                success_rate = 100*(int(result['details']['tests']) - int(result['details']['failures']))/int(result['details']['tests'])
            else:
                success_rate = 0

            result['details']["tests"] = nb_tests_run
            result['details']["Success rate"] = str(success_rate) + "%"

            # Criteria management
            # *******************
            crit_tests = False
            crit_rate = False
            crit_time = False

            # Expect that at least 200 tests are run
            if nb_tests_run > 200:
                crit_tests = True

            # Expect that at least 90% of success
            if success_rate > 90:
                crit_rate = True

            if result['details']['duration'] < 900:
                crit_time = True

            result['criteria'] = {'tests': crit_tests,
                                  'Success rate': crit_rate,
                                  'duration': crit_time}

            # error management
            # ****************

            # TODO get information from artefact based on build tag
            # to identify errors of the associated run
            # build tag needed to wget errors on the artifacts
            # the idea is to list the tests in errors and provide the link
            # towards complete artifact
            # another option will be to put the errors in the DB
            # (in the detail section)...
            result['errors'] = {'tests': "",
                                'Success rate': "",
                                'duration': ""}

    templateLoader = jinja2.FileSystemLoader(os.path.dirname(os.path.abspath(__file__)))
    templateEnv = jinja2.Environment(loader=templateLoader)

    TEMPLATE_FILE = "index-tempest-tmpl.html"
    template = templateEnv.get_template(TEMPLATE_FILE)

    outputText = template.render(scenario_results=scenario_results,
                                 items=items,
                                 installer=installer)

    with open("index-tempest-" + installer + ".html", "wb") as fh:
        fh.write(outputText)
