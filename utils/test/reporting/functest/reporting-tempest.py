from urllib2 import Request, urlopen, URLError
import json
import jinja2
import os

installers = ["apex", "compass", "fuel", "joid"]
items = ["tests", "Success rate", "duration"]

PERIOD = 7
print "Generate Tempest automatic reporting"
for installer in installers:
    # we consider the Tempest results of the last PERIOD days
    url = "http://testresults.opnfv.org/test/api/v1/results?case=Tempest"
    request = Request(url + '&period=' + str(PERIOD)
                      + '&installer=' + installer + '&version=master')

    try:
        response = urlopen(request)
        k = response.read()
        results = json.loads(k)
    except URLError, e:
        print 'No kittez. Got an error code:', e

    test_results = results['results']
    test_results.reverse()

    scenario_results = {}
    criteria = {}
    errors = {}

    for r in test_results:
        # Retrieve all the scenarios per installer
        # In Brahmaputra use version
        # Since Colorado use scenario
        if not r['scenario'] in scenario_results.keys():
            scenario_results[r['scenario']] = []
        scenario_results[r['scenario']].append(r)

    for s, s_result in scenario_results.items():
        scenario_results[s] = s_result[0:5]
        # For each scenario, we build a result object to deal with
        # results, criteria and error handling
        for result in scenario_results[s]:
            result["start_date"] = result["start_date"].split(".")[0]

            # retrieve results
            # ****************
            nb_tests_run = result['details']['tests']
            nb_tests_failed = result['details']['failures']
            if nb_tests_run != 0:
                success_rate = 100*(int(nb_tests_run)
                                    - int(nb_tests_failed))/int(nb_tests_run)
            else:
                success_rate = 0

            result['details']["tests"] = nb_tests_run
            result['details']["Success rate"] = str(success_rate) + "%"

            # Criteria management
            # *******************
            crit_tests = False
            crit_rate = False
            crit_time = False

            # Expect that at least 165 tests are run
            if nb_tests_run >= 165:
                crit_tests = True

            # Expect that at least 90% of success
            if success_rate >= 90:
                crit_rate = True

            # Expect that the suite duration is inferior to 30m
            if result['details']['duration'] < 1800:
                crit_time = True

            result['criteria'] = {'tests': crit_tests,
                                  'Success rate': crit_rate,
                                  'duration': crit_time}
            # error management
            # ****************
            try:
                errors = result['details']['errors']
                result['errors'] = errors.replace('{0}', '')
            except:
                print "Error field not present (Brahamputra runs?)"

    mypath = os.path.abspath(__file__)
    tplLoader = jinja2.FileSystemLoader(os.path.dirname(mypath))
    templateEnv = jinja2.Environment(loader=tplLoader)

    TEMPLATE_FILE = "./template/index-tempest-tmpl.html"
    template = templateEnv.get_template(TEMPLATE_FILE)

    outputText = template.render(scenario_results=scenario_results,
                                 items=items,
                                 installer=installer)

    with open("./release/master/index-tempest-" +
              installer + ".html", "wb") as fh:
        fh.write(outputText)
print "Tempest automatic reporting Done"
