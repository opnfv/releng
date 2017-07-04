from urllib2 import Request, urlopen, URLError
import json
import jinja2

# manage conf
import utils.reporting_utils as rp_utils

logger = rp_utils.getLogger("vIMS")


def sig_test_format(sig_test):
    nbPassed = 0
    nbFailures = 0
    nbSkipped = 0
    for data_test in sig_test:
        if data_test['result'] == "Passed":
            nbPassed += 1
        elif data_test['result'] == "Failed":
            nbFailures += 1
        elif data_test['result'] == "Skipped":
            nbSkipped += 1
    total_sig_test_result = {}
    total_sig_test_result['passed'] = nbPassed
    total_sig_test_result['failures'] = nbFailures
    total_sig_test_result['skipped'] = nbSkipped
    return total_sig_test_result

period = rp_utils.get_config('general.period')
versions = rp_utils.get_config('general.versions')
url_base = rp_utils.get_config('testapi.url')

logger.info("****************************************")
logger.info("*   Generating reporting vIMS          *")
logger.info("*   Data retention = %s days           *" % period)
logger.info("*                                      *")
logger.info("****************************************")

installers = rp_utils.get_config('general.installers')
step_order = ["initialisation", "orchestrator", "vIMS", "sig_test"]
logger.info("Start processing....")

# For all the versions
for version in versions:
    for installer in installers:
        logger.info("Search vIMS results for installer: %s, version: %s"
                    % (installer, version))
        request = Request("http://" + url_base + '?case=vims&installer=' +
                          installer + '&version=' + version)

        try:
            response = urlopen(request)
            k = response.read()
            results = json.loads(k)
        except URLError as e:
            logger.error("Error code: %s" % e)

        test_results = results['results']

        logger.debug("Results found: %s" % test_results)

        scenario_results = {}
        for r in test_results:
            if not r['scenario'] in scenario_results.keys():
                scenario_results[r['scenario']] = []
            scenario_results[r['scenario']].append(r)

        for s, s_result in scenario_results.items():
            scenario_results[s] = s_result[0:5]
            logger.debug("Search for success criteria")
            for result in scenario_results[s]:
                result["start_date"] = result["start_date"].split(".")[0]
                sig_test = result['details']['sig_test']['result']
                if not sig_test == "" and isinstance(sig_test, list):
                    format_result = sig_test_format(sig_test)
                    if format_result['failures'] > format_result['passed']:
                        result['details']['sig_test']['duration'] = 0
                    result['details']['sig_test']['result'] = format_result
                nb_step_ok = 0
                nb_step = len(result['details'])

                for step_name, step_result in result['details'].items():
                    if step_result['duration'] != 0:
                        nb_step_ok += 1
                    m, s = divmod(step_result['duration'], 60)
                    m_display = ""
                    if int(m) != 0:
                        m_display += str(int(m)) + "m "

                    step_result['duration_display'] = (m_display +
                                                       str(int(s)) + "s")

                result['pr_step_ok'] = 0
                if nb_step != 0:
                    result['pr_step_ok'] = (float(nb_step_ok) / nb_step) * 100
                try:
                    logger.debug("Scenario %s, Installer %s"
                                 % (s_result[1]['scenario'], installer))
                    res = result['details']['orchestrator']['duration']
                    logger.debug("Orchestrator deployment: %s s"
                                 % res)
                    logger.debug("vIMS deployment: %s s"
                                 % result['details']['vIMS']['duration'])
                    logger.debug("Signaling testing: %s s"
                                 % result['details']['sig_test']['duration'])
                    logger.debug("Signaling testing results: %s"
                                 % format_result)
                except Exception:
                    logger.error("Data badly formatted")
                logger.debug("----------------------------------------")

        templateLoader = jinja2.FileSystemLoader(".")
        templateEnv = jinja2.Environment(loader=templateLoader,
                                         autoescape=True)

        TEMPLATE_FILE = "./reporting/functest/template/index-vims-tmpl.html"
        template = templateEnv.get_template(TEMPLATE_FILE)

        outputText = template.render(scenario_results=scenario_results,
                                     step_order=step_order,
                                     installer=installer)

        with open("./display/" + version + "/functest/vims-" +
                  installer + ".html", "wb") as fh:
            fh.write(outputText)

logger.info("vIMS report succesfully generated")
