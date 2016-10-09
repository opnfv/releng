#! /usr/bin/env python

import datetime
import json
import os
import subprocess
import traceback
import urlparse
import uuid

import argparse

from common import logger_utils, elastic_access
from conf import testcases
from conf.config import APIConfig
from mongo2elastic import format

logger = logger_utils.DashboardLogger('mongo2elastic').get

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config-file",
                    dest='config_file',
                    help="Config file location")
parser.add_argument('-ld', '--latest-days',
                    default=0,
                    type=int,
                    metavar='N',
                    help='get entries old at most N days from mongodb and'
                         ' parse those that are not already in elasticsearch.'
                         ' If not present, will get everything from mongodb, which is the default')

args = parser.parse_args()
CONF = APIConfig().parse(args.config_file)


tmp_docs_file = './mongo-{}.json'.format(uuid.uuid4())


class DocumentVerification(object):
    def __init__(self, doc):
        super(DocumentVerification, self).__init__()
        self.doc = doc
        self.doc_id = doc['_id'] if '_id' in doc else None
        self.skip = False

    def mandatory_fields_exist(self):
        mandatory_fields = ['installer',
                            'pod_name',
                            'version',
                            'case_name',
                            'project_name',
                            'details',
                            'start_date',
                            'scenario']
        for key, value in self.doc.items():
            if key in mandatory_fields:
                if value is None:
                    logger.info("Skip testcase '%s' because field '%s' missing" %
                                (self.doc_id, key))
                    self.skip = True
                else:
                    mandatory_fields.remove(key)
            else:
                del self.doc[key]

        if len(mandatory_fields) > 0:
            logger.info("Skip testcase '%s' because field(s) '%s' missing" %
                        (self.doc_id, mandatory_fields))
            self.skip = True

        return self

    def modify_start_date(self):
        field = 'start_date'
        if field in self.doc:
            self.doc[field] = self._fix_date(self.doc[field])

        return self

    def modify_scenario(self):
        scenario = 'scenario'
        version = 'version'

        if (scenario not in self.doc) or \
                (scenario in self.doc and self.doc[scenario] is None):
            self.doc[scenario] = self.doc[version]

        return self

    def is_skip(self):
        return self.skip

    def _fix_date(self, date_string):
        if isinstance(date_string, dict):
            return date_string['$date']
        else:
            return date_string[:-3].replace(' ', 'T') + 'Z'


class DocumentPublisher(object):

    def __init__(self, doc, fmt, exist_docs, creds, elastic_url):
        self.doc = doc
        self.fmt = fmt
        self.creds = creds
        self.exist_docs = exist_docs
        self.elastic_url = elastic_url
        self.is_formatted = True

    def format(self):
        try:
            if self._verify_document() and self.fmt:
                self.is_formatted = vars(format)[self.fmt](self.doc)
            else:
                self.is_formatted = False
        except Exception:
            logger.error("Fail in format testcase[%s]\nerror message: %s" %
                         (self.doc, traceback.format_exc()))
            self.is_formatted = False
        finally:
            return self

    def publish(self):
        if self.is_formatted and self.doc not in self.exist_docs:
            self._publish()

    def _publish(self):
        status, data = elastic_access.publish_docs(self.elastic_url, self.creds, self.doc)
        if status > 300:
            logger.error('Publish record[{}] failed, due to [{}]'
                         .format(self.doc, json.loads(data)['error']['reason']))

    def _fix_date(self, date_string):
        if isinstance(date_string, dict):
            return date_string['$date']
        else:
            return date_string[:-3].replace(' ', 'T') + 'Z'

    def _verify_document(self):
        return not (DocumentVerification(self.doc)
                    .modify_start_date()
                    .modify_scenario()
                    .mandatory_fields_exist()
                    .is_skip())


class DocumentsPublisher(object):

    def __init__(self, project, case, fmt, days, elastic_url, creds):
        self.project = project
        self.case = case
        self.fmt = fmt
        self.days = days
        self.elastic_url = elastic_url
        self.creds = creds
        self.existed_docs = []

    def export(self):
        if self.days > 0:
            past_time = datetime.datetime.today() - datetime.timedelta(days=self.days)
            query = '''{{
                          "project_name": "{}",
                          "case_name": "{}",
                          "start_date": {{"$gt" : "{}"}}
                        }}'''.format(self.project, self.case, past_time)
        else:
            query = '''{{
                           "project_name": "{}",
                           "case_name": "{}"
                        }}'''.format(self.project, self.case)
        cmd = ['mongoexport',
               '--db', 'test_results_collection',
               '--collection', 'results',
               '--query', '{}'.format(query),
               '--out', '{}'.format(tmp_docs_file)]
        try:
            subprocess.check_call(cmd)
            return self
        except Exception, err:
            logger.error("export mongodb failed: %s" % err)
            self._remove()
            exit(-1)

    def get_existed_docs(self):
        if self.days == 0:
            body = '''{{
                        "query": {{
                            "bool": {{
                                "must": [
                                    {{ "match": {{ "project_name": "{}" }} }},
                                    {{ "match": {{ "case_name": "{}" }} }}
                                ]
                            }}
                        }}
                    }}'''.format(self.project, self.case)
        elif self.days > 0:
            body = '''{{
                       "query": {{
                           "bool": {{
                               "must": [
                                   {{ "match": {{ "project_name": "{}" }} }},
                                   {{ "match": {{ "case_name": "{}" }} }}
                               ],
                               "filter": {{
                                   "range": {{
                                       "start_date": {{ "gte": "now-{}d" }}
                                   }}
                               }}
                           }}
                       }}
                   }}'''.format(self.project, self.case, self.days)
        else:
            raise Exception('Update days must be non-negative')
        self.existed_docs = elastic_access.get_docs(self.elastic_url, self.creds, body)
        return self

    def publish(self):
        fdocs = None
        try:
            with open(tmp_docs_file) as fdocs:
                for doc_line in fdocs:
                    DocumentPublisher(json.loads(doc_line),
                                      self.fmt,
                                      self.existed_docs,
                                      self.creds,
                                      self.elastic_url).format().publish()
        finally:
            if fdocs:
                fdocs.close()
            self._remove()

    def _remove(self):
        if os.path.exists(tmp_docs_file):
            os.remove(tmp_docs_file)


def main():
    base_elastic_url = urlparse.urljoin(CONF.elastic_url, '/test_results/mongo2elastic')
    days = args.latest_days
    es_creds = CONF.elastic_creds

    for project, case_dicts in testcases.testcases_yaml.items():
        for case_dict in case_dicts:
            case = case_dict.get('name')
            fmt = testcases.compose_format(case_dict.get('format'))
            DocumentsPublisher(project,
                               case,
                               fmt,
                               days,
                               base_elastic_url,
                               es_creds).export().get_existed_docs().publish()
