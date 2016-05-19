from bson.objectid import ObjectId
from concurrent.futures import ThreadPoolExecutor

__author__ = 'serena'


class MemCursor(object):
    def __init__(self, collection):
        self.collection = collection
        self.count = len(self.collection)

    def _is_next_exist(self):
        return self.count != 0

    @property
    def fetch_next(self):
        with ThreadPoolExecutor(max_workers=2) as executor:
            result = executor.submit(self._is_next_exist)
        return result

    def next_object(self):
        self.count -= 1
        return self.collection.pop()


class MemDb(object):

    def __init__(self):
        self.contents = []
        pass

    def _find_one(self, spec_or_id=None, *args):
        if spec_or_id is not None and not isinstance(spec_or_id, dict):
            spec_or_id = {"_id": spec_or_id}
        cursor = self._find(spec_or_id, *args)
        for result in cursor:
            return result
        return None

    def find_one(self, spec_or_id=None, *args):
        with ThreadPoolExecutor(max_workers=2) as executor:
            result = executor.submit(self._find_one, spec_or_id, *args)
        return result

    def _insert(self, doc_or_docs):

        docs = doc_or_docs
        return_one = False
        if isinstance(docs, dict):
            return_one = True
            docs = [docs]

        ids = []
        for doc in docs:
            if '_id' not in doc:
                doc['_id'] = ObjectId()
            if not self._find_one(doc['_id']):
                ids.append(doc['_id'])
                self.contents.append(doc_or_docs)

        if len(ids) == 0:
            return None
        if return_one:
            return ids[0]
        else:
            return ids

    def insert(self, doc_or_docs):
        with ThreadPoolExecutor(max_workers=2) as executor:
            result = executor.submit(self._insert, doc_or_docs)
        return result

    @staticmethod
    def _in(content, *args):
        for arg in args:
            for k, v in arg.iteritems():
                if content.get(k, None) != v:
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

    def _update(self, spec, document):
        updated = False
        for index in range(len(self.contents)):
            content = self.contents[index]
            if self._in(content, spec):
                for k, v in document.iteritems():
                    updated = True
                    content[k] = v
            self.contents[index] = content
        return updated

    def update(self, spec, document):
        with ThreadPoolExecutor(max_workers=2) as executor:
            result = executor.submit(self._update, spec, document)
        return result

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
        with ThreadPoolExecutor(max_workers=2) as executor:
            result = executor.submit(self._remove, spec_or_id)
        return result

    def clear(self):
        self._remove()

pods = MemDb()
projects = MemDb()
test_cases = MemDb()
test_results = MemDb()
