#! /usr/bin/env python
import logging
import argparse
import shared_utils
import json
import urlparse
import uuid
import os
import subprocess
import datetime

logger = logging.getLogger('mongo_to_elasticsearch')
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('/var/log/{}.log'.format(__name__))
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
logger.addHandler(file_handler)


def _get_dicts_from_list(testcase, dict_list, keys):
    dicts = []
    for dictionary in dict_list:
        # iterate over dictionaries in input list
        if not isinstance(dictionary, dict):
            logger.info("Skipping non-dict details testcase [{}]".format(testcase))
            continue
        if keys == set(dictionary.keys()):
            # check the dictionary structure
            dicts.append(dictionary)
    return dicts


def _get_results_from_list_of_dicts(list_of_dict_statuses, dict_indexes, expected_results=None):
    test_results = {}
    for test_status in list_of_dict_statuses:
        status = test_status
        for index in dict_indexes:
            status = status[index]
        if status in test_results:
            test_results[status] += 1
        else:
            test_results[status] = 1

    if expected_results is not None:
        for expected_result in expected_results:
            if expected_result not in test_results:
                test_results[expected_result] = 0

    return test_results


def _convert_value(value):
    return value if value != '' else 0


def _convert_duration(duration):
    if (isinstance(duration, str) or isinstance(duration, unicode)) and ':' in duration:
        hours, minutes, seconds = duration.split(":")
        hours = _convert_value(hours)
        minutes = _convert_value(minutes)
        seconds = _convert_value(seconds)
        int_duration = 3600 * int(hours) + 60 * int(minutes) + float(seconds)
    else:
        int_duration = duration
    return int_duration


def modify_functest_tempest(testcase):
    if modify_default_entry(testcase):
        testcase_details = testcase['details']
        testcase_tests = float(testcase_details['tests'])
        testcase_failures = float(testcase_details['failures'])
        if testcase_tests != 0:
            testcase_details['success_percentage'] = 100 * (testcase_tests - testcase_failures) / testcase_tests
        else:
            testcase_details['success_percentage'] = 0
        return True
    else:
        return False


def modify_functest_vims(testcase):
    """
    Structure:
        details.sig_test.result.[{result}]
        details.sig_test.duration
        details.vIMS.duration
        details.orchestrator.duration

    Find data for these fields
        -> details.sig_test.duration
        -> details.sig_test.tests
        -> details.sig_test.failures
        -> details.sig_test.passed
        -> details.sig_test.skipped
        -> details.vIMS.duration
        -> details.orchestrator.duration
    """
    testcase_details = testcase['details']
    sig_test_results = _get_dicts_from_list(testcase, testcase_details['sig_test']['result'],
                                            {'duration', 'result', 'name', 'error'})
    if len(sig_test_results) < 1:
        logger.info("No 'result' from 'sig_test' found in vIMS details, skipping")
        return False
    else:
        test_results = _get_results_from_list_of_dicts(sig_test_results, ('result',), ('Passed', 'Skipped', 'Failed'))
        passed = test_results['Passed']
        skipped = test_results['Skipped']
        failures = test_results['Failed']
        all_tests = passed + skipped + failures
        testcase['details'] = {
            'sig_test': {
                'duration': testcase_details['sig_test']['duration'],
                'tests': all_tests,
                'failures': failures,
                'passed': passed,
                'skipped': skipped
            },
            'vIMS': {
                'duration': testcase_details['vIMS']['duration']
            },
            'orchestrator': {
                'duration': testcase_details['orchestrator']['duration']
            }
        }
        return True


def modify_functest_onos(testcase):
    """
    Structure:
        details.FUNCvirNet.duration
        details.FUNCvirNet.status.[{Case result}]
        details.FUNCvirNetL3.duration
        details.FUNCvirNetL3.status.[{Case result}]

    Find data for these fields
        -> details.FUNCvirNet.duration
        -> details.FUNCvirNet.tests
        -> details.FUNCvirNet.failures
        -> details.FUNCvirNetL3.duration
        -> details.FUNCvirNetL3.tests
        -> details.FUNCvirNetL3.failures
    """
    testcase_details = testcase['details']

    funcvirnet_details = testcase_details['FUNCvirNet']['status']
    funcvirnet_statuses = _get_dicts_from_list(testcase, funcvirnet_details, {'Case result', 'Case name:'})

    funcvirnetl3_details = testcase_details['FUNCvirNetL3']['status']
    funcvirnetl3_statuses = _get_dicts_from_list(testcase, funcvirnetl3_details, {'Case result', 'Case name:'})

    if len(funcvirnet_statuses) < 0:
        logger.info("No results found in 'FUNCvirNet' part of ONOS results")
        return False
    elif len(funcvirnetl3_statuses) < 0:
        logger.info("No results found in 'FUNCvirNetL3' part of ONOS results")
        return False
    else:
        funcvirnet_results = _get_results_from_list_of_dicts(funcvirnet_statuses,
                                                             ('Case result',), ('PASS', 'FAIL'))
        funcvirnetl3_results = _get_results_from_list_of_dicts(funcvirnetl3_statuses,
                                                               ('Case result',), ('PASS', 'FAIL'))

        funcvirnet_passed = funcvirnet_results['PASS']
        funcvirnet_failed = funcvirnet_results['FAIL']
        funcvirnet_all = funcvirnet_passed + funcvirnet_failed

        funcvirnetl3_passed = funcvirnetl3_results['PASS']
        funcvirnetl3_failed = funcvirnetl3_results['FAIL']
        funcvirnetl3_all = funcvirnetl3_passed + funcvirnetl3_failed

        testcase_details['FUNCvirNet'] = {
            'duration': _convert_duration(testcase_details['FUNCvirNet']['duration']),
            'tests': funcvirnet_all,
            'failures': funcvirnet_failed
        }

        testcase_details['FUNCvirNetL3'] = {
            'duration': _convert_duration(testcase_details['FUNCvirNetL3']['duration']),
            'tests': funcvirnetl3_all,
            'failures': funcvirnetl3_failed
        }

        return True


def modify_functest_rally(testcase):
    """
    Structure:
        details.[{summary.duration}]
        details.[{summary.nb success}]
        details.[{summary.nb tests}]

    Find data for these fields
        -> details.duration
        -> details.tests
        -> details.success_percentage
    """
    summaries = _get_dicts_from_list(testcase, testcase['details'], {'summary'})

    if len(summaries) != 1:
        logger.info("Found zero or more than one 'summaries' in Rally details, skipping")
        return False
    else:
        summary = summaries[0]['summary']
        testcase['details'] = {
            'duration': summary['duration'],
            'tests': summary['nb tests'],
            'success_percentage': summary['nb success']
        }
        return True


def modify_functest_odl(testcase):
    """
    Structure:
        details.details.[{test_status.@status}]

    Find data for these fields
        -> details.tests
        -> details.failures
        -> details.success_percentage?
    """
    test_statuses = _get_dicts_from_list(testcase, testcase['details']['details'],
                                         {'test_status', 'test_doc', 'test_name'})
    if len(test_statuses) < 1:
        logger.info("No 'test_status' found in ODL details, skipping")
        return False
    else:
        test_results = _get_results_from_list_of_dicts(test_statuses, ('test_status', '@status'), ('PASS', 'FAIL'))

        passed_tests = test_results['PASS']
        failed_tests = test_results['FAIL']
        all_tests = passed_tests + failed_tests

        testcase['details'] = {
            'tests': all_tests,
            'failures': failed_tests,
            'success_percentage': 100 * passed_tests / float(all_tests)
        }
        return True


def modify_default_entry(testcase):
    """
    Look for these and leave any of those:
        details.duration
        details.tests
        details.failures

    If none are present, then return False
    """
    found = False
    testcase_details = testcase['details']
    fields = ['duration', 'tests', 'failures']
    if isinstance(testcase_details, dict):
        for key, value in testcase_details.items():
            if key in fields:
                found = True
                if key == 'duration':
                    testcase_details[key] = _convert_duration(value)
            else:
                del testcase_details[key]

    return found


def _fix_date(date_string):
    if isinstance(date_string, dict):
        return date_string['$date']
    else:
        return date_string[:-3].replace(' ', 'T') + 'Z'


def verify_mongo_entry(testcase):
    """
    Mandatory fields:
        installer
        pod_name
        version
        case_name
        date
        project
        details

        these fields must be present and must NOT be None

    Optional fields:
        description

        these fields will be preserved if the are NOT None
    """
    mandatory_fields = ['installer',
                        'pod_name',
                        'version',
                        'case_name',
                        'project_name',
                        'details']
    mandatory_fields_to_modify = {'creation_date': _fix_date}
    if '_id' in testcase:
        mongo_id = testcase['_id']
    else:
        mongo_id = None
    optional_fields = ['description']
    for key, value in testcase.items():
        if key in mandatory_fields:
            if value is None:
                # empty mandatory field, invalid input
                logger.info("Skipping testcase with mongo _id '{}' because the testcase was missing value"
                            " for mandatory field '{}'".format(mongo_id, key))
                return False
            else:
                mandatory_fields.remove(key)
        elif key in mandatory_fields_to_modify:
            if value is None:
                # empty mandatory field, invalid input
                logger.info("Skipping testcase with mongo _id '{}' because the testcase was missing value"
                            " for mandatory field '{}'".format(mongo_id, key))
                return False
            else:
                testcase[key] = mandatory_fields_to_modify[key](value)
                del mandatory_fields_to_modify[key]
        elif key in optional_fields:
            if value is None:
                # empty optional field, remove
                del testcase[key]
            optional_fields.remove(key)
        else:
            # unknown field
            del testcase[key]

    if len(mandatory_fields) > 0:
        # some mandatory fields are missing
        logger.info("Skipping testcase with mongo _id '{}' because the testcase was missing"
                    " mandatory field(s) '{}'".format(mongo_id, mandatory_fields))
        return False
    else:
        return True


def modify_mongo_entry(testcase):
    # 1. verify and identify the testcase
    # 2. if modification is implemented, then use that
    # 3. if not, try to use default
    # 4. if 2 or 3 is successful, return True, otherwise return False
    if verify_mongo_entry(testcase):
        project = testcase['project_name']
        case_name = testcase['case_name']
        if project == 'functest':
            if case_name == 'Rally':
                return modify_functest_rally(testcase)
            elif case_name == 'ODL':
                return modify_functest_odl(testcase)
            elif case_name == 'ONOS':
                return modify_functest_onos(testcase)
            elif case_name == 'vIMS':
                return modify_functest_vims(testcase)
            elif case_name == 'Tempest':
                return modify_functest_tempest(testcase)
        return modify_default_entry(testcase)
    else:
        return False


def publish_mongo_data(output_destination):
    tmp_filename = 'mongo-{}.log'.format(uuid.uuid4())
    try:
        subprocess.check_call(['mongoexport', '--db', 'test_results_collection', '-c', 'test_results', '--out',
                               tmp_filename])
        with open(tmp_filename) as fobj:
            for mongo_json_line in fobj:
                test_result = json.loads(mongo_json_line)
                if modify_mongo_entry(test_result):
                    shared_utils.publish_json(test_result, es_user, es_passwd, output_destination)
    finally:
        if os.path.exists(tmp_filename):
            os.remove(tmp_filename)


def get_mongo_data(days):
    past_time = datetime.datetime.today() - datetime.timedelta(days=days)
    mongo_json_lines = subprocess.check_output(['mongoexport', '--db', 'test_results_collection', '-c', 'test_results',
                                                '--query', '{{"creation_date":{{$gt:"{}"}}}}'
                                               .format(past_time)]).splitlines()

    mongo_data = []
    for mongo_json_line in mongo_json_lines:
        test_result = json.loads(mongo_json_line)
        if modify_mongo_entry(test_result):
            # if the modification could be applied, append the modified result
            mongo_data.append(test_result)
    return mongo_data


def publish_difference(mongo_data, elastic_data, output_destination, es_user, es_passwd):
    for elastic_entry in elastic_data:
        if elastic_entry in mongo_data:
            mongo_data.remove(elastic_entry)

    logger.info('number of parsed test results: {}'.format(len(mongo_data)))

    for parsed_test_result in mongo_data:
        shared_utils.publish_json(parsed_test_result, es_user, es_passwd, output_destination)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Modify and filter mongo json data for elasticsearch')
    parser.add_argument('-od', '--output-destination',
                        default='elasticsearch',
                        choices=('elasticsearch', 'stdout'),
                        help='defaults to elasticsearch')

    parser.add_argument('-ml', '--merge-latest', default=0, type=int, metavar='N',
                        help='get entries old at most N days from mongodb and'
                             ' parse those that are not already in elasticsearch.'
                             ' If not present, will get everything from mongodb, which is the default')

    parser.add_argument('-e', '--elasticsearch-url', default='http://localhost:9200',
                        help='the url of elasticsearch, defaults to http://localhost:9200')

    parser.add_argument('-u', '--elasticsearch-username',
                        help='the username for elasticsearch')

    parser.add_argument('-p', '--elasticsearch-password',
                        help='the password for elasticsearch')

    parser.add_argument('-m', '--mongodb-url', default='http://localhost:8082',
                        help='the url of mongodb, defaults to http://localhost:8082')

    args = parser.parse_args()
    base_elastic_url = urlparse.urljoin(args.elasticsearch_url, '/test_results/mongo2elastic')
    output_destination = args.output_destination
    days = args.merge_latest
    es_user = args.elasticsearch_username
    es_passwd = args.elasticsearch_password

    if output_destination == 'elasticsearch':
        output_destination = base_elastic_url

    # parsed_test_results will be printed/sent to elasticsearch
    if days == 0:
        # TODO get everything from mongo
        publish_mongo_data(output_destination)
    elif days > 0:
        body = '''{{
    "query" : {{
        "range" : {{
            "creation_date" : {{
                "gte" : "now-{}d"
            }}
        }}
    }}
}}'''.format(days)
        elastic_data = shared_utils.get_elastic_data(base_elastic_url, es_user, es_passwd, body)
        logger.info('number of hits in elasticsearch for now-{}d: {}'.format(days, len(elastic_data)))
        mongo_data = get_mongo_data(days)
        publish_difference(mongo_data, elastic_data, output_destination, es_user, es_passwd)
    else:
        raise Exception('Update must be non-negative')
