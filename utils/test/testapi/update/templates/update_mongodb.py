##############################################################################
# Copyright (c) 2016 ZTE Corporation
# feng.xiaowei@zte.com.cn
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import argparse

from pymongo import MongoClient

from changes_in_mongodb import collections_old2New, \
    fields_old2New, docs_old2New
from utils import main, parse_mongodb_url

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


def assert_collections(a_dict):
    if a_dict is not None:
        collections = eval_db('collection_names')
        no_collections = []
        for collection in a_dict.keys():
            if collection not in collections:
                no_collections.append(collection)
        assert len(no_collections) == 0, \
            'collections {} not exist'.format(no_collections)


def rename_collections(a_dict):
    if a_dict is not None:
        for collection, new_name in a_dict.iteritems():
            eval_collection(collection, 'rename', new_name)


def rename_fields(a_dict):
    collection_update(a_dict, '$rename')


def change_docs(a_dict):
    collection_update(a_dict, '$set')


def eval_db(method, *args, **kwargs):
    exec_db = db.__getattribute__(method)
    return exec_db(*args, **kwargs)


def eval_collection(collection, method, *args, **kwargs):
    exec_collection = db.__getattr__(collection)
    return exec_collection.__getattribute__(method)(*args, **kwargs)


def collection_update(a_dict, operator):
    if a_dict is not None:
        for collection, updates in a_dict.iteritems():
            for (query, doc) in updates:
                doc_dict = {operator: doc}
                eval_collection(collection, 'update', query,
                                doc_dict, upsert=False, multi=True)


def update(args):
    parse_mongodb_url(args.url)
    client = MongoClient(args.url)
    global db
    db = client[args.db]
    assert_collections(docs_old2New)
    assert_collections(fields_old2New)
    assert_collections(collections_old2New)
    change_docs(docs_old2New)
    rename_fields(fields_old2New)
    rename_collections(collections_old2New)


if __name__ == '__main__':
    main(update, parser)
