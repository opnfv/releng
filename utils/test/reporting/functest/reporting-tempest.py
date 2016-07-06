from urllib2 import Request, urlopen, URLError
import json
import jinja2
import reportingConf as conf
import reportingUtils as utils

installers = conf.installers
items = ["tests", "Success rate", "duration"]

PERIOD = conf.PERIOD
criteria_nb_test = 165
criteria_duration = 1800
criteria_success_rate = 90

logger = utils.getLogger("Tempest")
logger.info("************************************************")
logger.info("*   Generating reporting Tempest_smoke_serial  *")
logger.info("*   Data retention = %s days                   *" % PERIOD)
logger.info("*                                              *")
logger.info("************************************************")

logger.info("Success criteria: nb tests executed > %s s," +
            "test duration < %s s," +
            "success rate > %s " % (criteria_nb_test,
                                    criteria_duration,
                                    criteria_success_rate))

for installer in installers:
    # we consider the Tempest results of the last PERIOD days
    url = conf.URL_BASE + "?case=tempest_smoke_serial"
    request = Request(url + '&period=' + str(PERIOD) +
                      '&installer=' + installer + '&version=master')
    logger.info("Search tempest_smoke_serial results for installer %s"
                % installer)
    try:
        response = urlopen(request)
        k = response.read()
        results = json.loads(k)
    except URLError, e:
        logger.error("Error code: %s" % e)

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
                success_rate = 100*(int(nb_tests_run) -
                                    int(nb_tests_failed)) / int(nb_tests_run)
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
            if nb_tests_run >= criteria_nb_test:
                crit_tests = True

            # Expect that at least 90% of success
            if success_rate >= criteria_success_rate:
                crit_rate = True

            # Expect that the suite duration is inferior to 30m
            if result['details']['duration'] < criteria_duration:
                crit_time = True

            result['criteria'] = {'tests': crit_tests,
                                  'Success rate': crit_rate,
                                  'duration': crit_time}
            try:
                logger.debug("Scenario %s, Installer %s"
                             % (s_result[1]['scenario'], installer))
                logger.debug("Nb Test run: %s" % nb_tests_run)
                logger.debug("Test duration: %s"
                             % result['details']['duration'])
                logger.debug("Success rate: %s" % success_rate)
            except:
                logger.error("Data format error")

            # Error management
            # ****************
            try:
                errors = result['details']['errors']
                result['errors'] = errors.replace('{0}', '')
            except:
                logger.error("Error field not present (Brahamputra runs?)")

    templateLoader = jinja2.FileSystemLoader(conf.REPORTING_PATH)
    templateEnv = jinja2.Environment(loader=templateLoader)

    TEMPLATE_FILE = "/template/index-tempest-tmpl.html"
    template = templateEnv.get_template(TEMPLATE_FILE)

    outputText = template.render(scenario_results=scenario_results,
                                 items=items,
                                 installer=installer)

    with open(conf.REPORTING_PATH + "/release/master/index-tempest-" +
              installer + ".html", "wb") as fh:
        fh.write(outputText)
logger.info("Tempest automatic reporting succesfully generated.")
