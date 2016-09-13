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

tmp_docs_file = './mongo-{}.json'.format(uuid.uuid4())


def _fix_date(date_string):
    if isinstance(date_string, dict):
        return date_string['$date']
    else:
        return date_string[:-3].replace(' ', 'T') + 'Z'


def verify_document(testcase):
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


def format_document(testcase):
    # 1. verify and identify the testcase
    # 2. if modification is implemented, then use that
    # 3. if not, try to use default
    # 4. if 2 or 3 is successful, return True, otherwise return False
    if verify_document(testcase):
        project = testcase['project_name']
        case_name = testcase['case_name']
        fmt = conf_utils.get_format(project, case_name)
        if fmt:
            try:
                logger.info("Processing %s/%s using format %s" % (project, case_name, fmt))
                return vars(mongo2elastic_format)[fmt](testcase)
            except Exception:
                logger.error("Fail in format testcase[%s]\nerror message: %s" % (testcase, traceback.format_exc()))
                return False
    else:
        return False


def export_documents(days):
    cmd = ['mongoexport', '--db', 'test_results_collection', '-c', 'results']
    if days > 0:
        past_time = datetime.datetime.today() - datetime.timedelta(days=days)
        cmd += ['--query', '{{"start_date":{{$gt:"{}"}}}}'.format(past_time)]
    cmd += [ '--out', '{}'.format(tmp_docs_file)]

    try:
        subprocess.check_call(cmd)
    except Exception, err:
        logger.error("export mongodb failed: %s" % err)
        exit(-1)


def publish_document(document, es_creds, to):
    status, data = shared_utils.publish_json(document, es_creds, to)
    if status > 300:
        logger.error('Publish record[{}] failed, due to [{}]'
                    .format(document, json.loads(data)['error']['reason']))


def publish_nonexist_documents(elastic_docs, es_creds, to):
    try:
        with open(tmp_docs_file) as fdocs:
            for doc_line in fdocs:
                doc = json.loads(doc_line)
                if format_document(doc) and doc not in elastic_docs:
                    publish_document(doc, es_creds, to)
    finally:
        fdocs.close()
        if os.path.exists(tmp_docs_file):
            os.remove(tmp_docs_file)


if __name__ == '__main__':
    base_elastic_url = urlparse.urljoin(args.elasticsearch_url, '/test_results/mongo2elastic')
    to = args.output_destination
    days = args.merge_latest
    es_creds = args.elasticsearch_username

    if to == 'elasticsearch':
        to = base_elastic_url

    export_documents(days)
    elastic_docs = shared_utils.get_elastic_docs_by_days(base_elastic_url, es_creds, days)
    logger.info('number of hits in elasticsearch for now-{}d: {}'.format(days, len(elastic_docs)))
    publish_nonexist_documents(elastic_docs, es_creds, to)
