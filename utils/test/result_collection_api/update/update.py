import argparse

from pymongo import MongoClient

from utils import main, parse_mongodb_url

db = None
parser = argparse.ArgumentParser(description='Update MongoDBs')

parser.add_argument('-u', '--url',
                    type=str,
                    required=False,
                    default='mongodb://127.0.0.1:27017/',
                    help='Mongo DB URL for Backups')

parser.add_argument('-d', '--db',
                    type=str,
                    required=False,
                    default='test_results_collection',
                    help='database for the update.')


def eval_db(method, *args, **kwargs):
    return eval('db.%s(*args, **kwargs)' % (method))


def eval_collection(collection, method, *args, **kwargs):
    print('db.%s.%s(*args, **kwargs)' % (collection, method))
    return eval('db.%s.%s(*args, **kwargs)' % (collection, method))


def assert_collections(a_dict):
    collections = eval_db('collection_names')
    no_collections = []
    for collection in a_dict.keys():
        if collection not in collections:
            no_collections.append(collection)
    assert len(no_collections) == 0, \
        'collections {} not exist'.format(no_collections)


def rename_collections(a_dict):
    if a_dict is not None:
        for k, v in a_dict.iteritems():
            eval_collection(k, 'rename', v)


def rename_fields(a_dict):
    if a_dict is not None:
        for k, v in a_dict.iteritems():
            v = {'$rename': v}
            eval_collection(k, 'update', {}, v, upsert=False, multi=True)


collections_old2New = {
        'pod': 'pods',
        'test_projects': 'projects',
        'test_testcases': 'testcases',
        'test_results': 'results'
}

collections_old2New2 = {
        'pods': 'pod',
        'projects': 'test_projects',
        'testcases': 'test_testcases',
        'results': 'test_results'
}

fields_old2New2 = {
    'test_results': {'start_date': 'creation_date'}
}

fields_old2New = {
    'results': {'creation_date': 'start_date'}
}


def update(args):
    parse_mongodb_url(args.url)
    client = MongoClient(args.url)
    db = client[args.db]
    assert_collections(collections_old2New)
    assert_collections(fields_old2New)
    rename_collections(collections_old2New)
    rename_fields(fields_old2New)

if __name__ == '__main__':
    main(update, parser)
