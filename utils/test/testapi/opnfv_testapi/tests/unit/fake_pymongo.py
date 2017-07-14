##############################################################################
# Copyright (c) 2016 ZTE Corporation
# feng.xiaowei@zte.com.cn
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
from operator import itemgetter

from bson.objectid import ObjectId
from concurrent.futures import ThreadPoolExecutor


def thread_execute(method, *args, **kwargs):
        with ThreadPoolExecutor(max_workers=2) as executor:
            result = executor.submit(method, *args, **kwargs)
        return result


class MemCursor(object):
    def __init__(self, collection):
        self.collection = collection
        self.length = len(self.collection)
        self.sorted = []

    def _is_next_exist(self):
        return self.length != 0

    @property
    def fetch_next(self):
        return thread_execute(self._is_next_exist)

    def next_object(self):
        self.length -= 1
        return self.collection.pop()

    def sort(self, key_or_list):
        for k, v in key_or_list.iteritems():
            if v == -1:
                reverse = True
            else:
                reverse = False

            self.collection = sorted(self.collection,
                                     key=itemgetter(k), reverse=reverse)
        return self

    def limit(self, limit):
        if limit != 0 and limit < len(self.collection):
            self.collection = self.collection[0: limit]
            self.length = limit
        return self

    def skip(self, skip):
        if skip < self.length and (skip > 0):
            self.collection = self.collection[self.length - skip: -1]
            self.length -= skip
        elif skip >= self.length:
            self.collection = []
            self.length = 0
        return self

    def _count(self):
        return self.length

    def count(self):
        return thread_execute(self._count)


class MemDb(object):

    def __init__(self, name):
        self.name = name
        self.contents = []
        pass

    def _find_one(self, spec_or_id=None, *args):
        if spec_or_id is not None and not isinstance(spec_or_id, dict):
            spec_or_id = {"_id": spec_or_id}
        if '_id' in spec_or_id:
            spec_or_id['_id'] = str(spec_or_id['_id'])
        cursor = self._find(spec_or_id, *args)
        for result in cursor:
            return result
        return None

    def find_one(self, spec_or_id=None, *args):
        return thread_execute(self._find_one, spec_or_id, *args)

    def _insert(self, doc_or_docs, check_keys=True):

        docs = doc_or_docs
        return_one = False
        if isinstance(docs, dict):
            return_one = True
            docs = [docs]

        if check_keys:
            for doc in docs:
                self._check_keys(doc)

        ids = []
        for doc in docs:
            if '_id' not in doc:
                doc['_id'] = str(ObjectId())
            if not self._find_one(doc['_id']):
                ids.append(doc['_id'])
                self.contents.append(doc_or_docs)

        if len(ids) == 0:
            return None
        if return_one:
            return ids[0]
        else:
            return ids

    def insert(self, doc_or_docs, check_keys=True):
        return thread_execute(self._insert, doc_or_docs, check_keys)

    @staticmethod
    def _compare_date(spec, value):
        gte = True
        lt = False
        for k, v in spec.iteritems():
            if k == '$gte' and value < v:
                gte = False
            elif k == '$lt' and value < v:
                lt = True
        return gte and lt

    def _in(self, content, *args):
        if self.name == 'scenarios':
            return self._in_scenarios(content, *args)
        else:
            return self._in_others(content, *args)

    def _in_scenarios_installer(self, installer, content):
        hit = False
        for s_installer in content['installers']:
            if installer == s_installer['installer']:
                hit = True

        return hit

    def _in_scenarios_version(self, version, content):
        hit = False
        for s_installer in content['installers']:
            for s_version in s_installer['versions']:
                if version == s_version['version']:
                    hit = True
        return hit

    def _in_scenarios_project(self, project, content):
        hit = False
        for s_installer in content['installers']:
            for s_version in s_installer['versions']:
                for s_project in s_version['projects']:
                    if project == s_project['project']:
                        hit = True

        return hit

    def _in_scenarios(self, content, *args):
        for arg in args:
            for k, v in arg.iteritems():
                if k == 'installers':
                    for inner in v.values():
                        for i_k, i_v in inner.iteritems():
                            if i_k == 'installer':
                                return self._in_scenarios_installer(i_v,
                                                                    content)
                            elif i_k == 'versions.version':
                                return self._in_scenarios_version(i_v,
                                                                  content)
                            elif i_k == 'versions.projects.project':
                                return self._in_scenarios_project(i_v,
                                                                  content)
                elif content.get(k, None) != v:
                    return False

        return True

    def _in_others(self, content, *args):
        for arg in args:
            for k, v in arg.iteritems():
                if k == 'start_date':
                    if not MemDb._compare_date(v, content.get(k)):
                        return False
                elif k == 'trust_indicator.current':
                    if content.get('trust_indicator').get('current') != v:
                        return False
                elif not isinstance(v, dict) and content.get(k, None) != v:
                    return False
        return True

    def _find(self, *args):
        res = []
        for content in self.contents:
            if self._in(content, *args):
                res.append(content)

        return res

    def find(self, *args):
        return MemCursor(self._find(*args))

    def _aggregate(self, *args, **kwargs):
        res = self.contents
        print args
        for arg in args[0]:
            for k, v in arg.iteritems():
                if k == '$match':
                    res = self._find(v)
        cursor = MemCursor(res)
        for arg in args[0]:
            for k, v in arg.iteritems():
                if k == '$sort':
                    cursor = cursor.sort(v)
                elif k == '$skip':
                    cursor = cursor.skip(v)
                elif k == '$limit':
                    cursor = cursor.limit(v)
        return cursor

    def aggregate(self, *args, **kwargs):
        return self._aggregate(*args, **kwargs)

    def _update(self, spec, document, check_keys=True):
        updated = False

        if check_keys:
            self._check_keys(document)

        for index in range(len(self.contents)):
            content = self.contents[index]
            if self._in(content, spec):
                for k, v in document.iteritems():
                    updated = True
                    content[k] = v
            self.contents[index] = content
        return updated

    def update(self, spec, document, check_keys=True):
        return thread_execute(self._update, spec, document, check_keys)

    def _remove(self, spec_or_id=None):
        if spec_or_id is None:
            self.contents = []
        if not isinstance(spec_or_id, dict):
            spec_or_id = {'_id': spec_or_id}
        for index in range(len(self.contents)):
            content = self.contents[index]
            if self._in(content, spec_or_id):
                del self.contents[index]
                return True
        return False

    def remove(self, spec_or_id=None):
        return thread_execute(self._remove, spec_or_id)

    def clear(self):
        self._remove()

    def _check_keys(self, doc):
        for key in doc.keys():
            if '.' in key:
                raise NameError('key {} must not contain .'.format(key))
            if key.startswith('$'):
                raise NameError('key {} must not start with $'.format(key))
            if isinstance(doc.get(key), dict):
                self._check_keys(doc.get(key))


def __getattr__(name):
    return globals()[name]


pods = MemDb('pods')
projects = MemDb('projects')
testcases = MemDb('testcases')
results = MemDb('results')
scenarios = MemDb('scenarios')
tokens = MemDb('tokens')
