#! /usr/bin/env python
import datetime
import json
import os
import subprocess
import traceback
import urlparse
import uuid

import argparse

import conf_utils
import logger_utils
import mongo2elastic_format
import shared_utils

logger = logger_utils.KibanaDashboardLogger('mongo2elastic').get


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
    mandatory_fields_to_modify = {'start_date': _fix_date}
    fields_to_swap_or_add = {'scenario': 'version'}
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
        elif key in fields_to_swap_or_add:
            if value is None:
                swapped_key = fields_to_swap_or_add[key]
                swapped_value = testcase[swapped_key]
                logger.info("Swapping field '{}' with value None for '{}' with value '{}'.".format(key, swapped_key, swapped_value))
                testcase[key] = swapped_value
                del fields_to_swap_or_add[key]
            else:
                del fields_to_swap_or_add[key]
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
    elif len(mandatory_fields_to_modify) > 0:
        # some mandatory fields are missing
        logger.info("Skipping testcase with mongo _id '{}' because the testcase was missing"
                    " mandatory field(s) '{}'".format(mongo_id, mandatory_fields_to_modify.keys()))
        return False
    else:
        if len(fields_to_swap_or_add) > 0:
            for key, swap_key in fields_to_swap_or_add.iteritems():
                testcase[key] = testcase[swap_key]

        return True


def modify_mongo_entry(testcase):
    # 1. verify and identify the testcase
    # 2. if modification is implemented, then use that
    # 3. if not, try to use default
    # 4. if 2 or 3 is successful, return True, otherwise return False
    if verify_mongo_entry(testcase):
        project = testcase['project_name']
        case_name = testcase['case_name']
        fmt = conf_utils.get_format(project, case_name)
        if fmt:
            try:
                logger.info("Processing %s/%s using format %s" % (project, case_name, fmt))
                return vars(mongo2elastic_format)[fmt](testcase)
            except Exception:
                logger.error("Fail in modify testcase[%s]\nerror message: %s" % (testcase, traceback.format_exc()))
    else:
        return False


def publish_mongo_data(output_destination):
    tmp_filename = 'mongo-{}.log'.format(uuid.uuid4())
    try:
        subprocess.check_call(['mongoexport',
                               '--db', 'test_results_collection',
                               '-c', 'results',
                               '--out', tmp_filename])
        with open(tmp_filename) as fobj:
            for mongo_json_line in fobj:
                test_result = json.loads(mongo_json_line)
                if modify_mongo_entry(test_result):
                    status, data = shared_utils.publish_json(test_result, es_creds, output_destination)
                    if status > 300:
                        project = test_result['project_name']
                        case_name = test_result['case_name']
                        logger.info('project {} case {} publish failed, due to [{}]'
                                    .format(project, case_name, json.loads(data)['error']['reason']))
    finally:
        if os.path.exists(tmp_filename):
            os.remove(tmp_filename)


def get_mongo_data(days):
    past_time = datetime.datetime.today() - datetime.timedelta(days=days)
    mongo_json_lines = subprocess.check_output(['mongoexport', '--db', 'test_results_collection', '-c', 'results',
                                                '--query', '{{"start_date":{{$gt:"{}"}}}}'
                                               .format(past_time)]).splitlines()

    mongo_data = []
    for mongo_json_line in mongo_json_lines:
        test_result = json.loads(mongo_json_line)
        if modify_mongo_entry(test_result):
            # if the modification could be applied, append the modified result
            mongo_data.append(test_result)
    return mongo_data


def publish_difference(mongo_data, elastic_data, output_destination, es_creds):
    for elastic_entry in elastic_data:
        if elastic_entry in mongo_data:
            mongo_data.remove(elastic_entry)

    logger.info('number of parsed test results: {}'.format(len(mongo_data)))

    for parsed_test_result in mongo_data:
        shared_utils.publish_json(parsed_test_result, es_creds, output_destination)


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

    parser.add_argument('-u', '--elasticsearch-username', default=None,
                        help='The username with password for elasticsearch in format username:password')

    args = parser.parse_args()
    base_elastic_url = urlparse.urljoin(args.elasticsearch_url, '/test_results/mongo2elastic')
    output_destination = args.output_destination
    days = args.merge_latest
    es_creds = args.elasticsearch_username

    if output_destination == 'elasticsearch':
        output_destination = base_elastic_url

    # parsed_test_results will be printed/sent to elasticsearch
    if days == 0:
        publish_mongo_data(output_destination)
    elif days > 0:
        body = '''{{
    "query" : {{
        "range" : {{
            "start_date" : {{
                "gte" : "now-{}d"
            }}
        }}
    }}
}}'''.format(days)
        elastic_data = shared_utils.get_elastic_data(base_elastic_url, es_creds, body)
        logger.info('number of hits in elasticsearch for now-{}d: {}'.format(days, len(elastic_data)))
        mongo_data = get_mongo_data(days)
        publish_difference(mongo_data, elastic_data, output_destination, es_creds)
    else:
        raise Exception('Update must be non-negative')

