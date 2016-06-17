from urllib2 import Request, urlopen, URLError
import json
import jinja2
import os

def sig_test_format(sig_test):
    nbPassed = 0
    nbFailures = 0
    nbSkipped = 0
    for data_test in sig_test:
        if data_test['result'] == "Passed":
            nbPassed+= 1
        elif data_test['result'] == "Failed":
            nbFailures += 1
        elif data_test['result'] == "Skipped":
            nbSkipped += 1
    total_sig_test_result = {}
    total_sig_test_result['passed'] = nbPassed
    total_sig_test_result['failures'] = nbFailures
    total_sig_test_result['skipped'] = nbSkipped
    return total_sig_test_result

installers = ["fuel", "compass", "joid", "apex"]
step_order = ["initialisation", "orchestrator", "vIMS", "sig_test"]

for installer in installers:
    request = Request('http://testresults.opnfv.org/test/api/v1/results?case=vims&installer=' + installer)

    try:
        response = urlopen(request)
        k = response.read()
        results = json.loads(k)
    except URLError, e:
        print 'No kittez. Got an error code:', e

    test_results = results['results']

    scenario_results = {}
    for r in test_results:
        if not r['version'] in scenario_results.keys():
            scenario_results[r['version']] = []
        scenario_results[r['version']].append(r)

    for s, s_result in scenario_results.items():
        scenario_results[s] = s_result[0:5]
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
                step_result['duration_display'] = m_display + str(int(s)) + "s"

            result['pr_step_ok'] = 0
            if nb_step != 0:
                result['pr_step_ok'] = (float(nb_step_ok)/nb_step)*100


    templateLoader = jinja2.FileSystemLoader(os.path.dirname(os.path.abspath(__file__)))
    templateEnv = jinja2.Environment( loader=templateLoader )

    TEMPLATE_FILE = "./template/index-vims-tmpl.html"
    template = templateEnv.get_template( TEMPLATE_FILE )

    outputText = template.render( scenario_results = scenario_results, step_order = step_order, installer = installer)

    with open("./release/master/index-vims-" + installer + ".html", "wb") as fh:
        fh.write(outputText)


