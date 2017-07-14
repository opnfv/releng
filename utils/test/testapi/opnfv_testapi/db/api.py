import motor

from opnfv_testapi.common.config import CONF

DB = motor.MotorClient(CONF.mongo_url)[CONF.mongo_dbname]


def db_update(collection, query, update_req):
    return _eval_db(collection, 'update', query, update_req, check_keys=False)


def db_delete(collection, query):
    return _eval_db(collection, 'remove', query)


def db_aggregate(collection, pipelines):
    return _eval_db(collection, 'aggregate', pipelines, allowDiskUse=True)


def db_list(collection, query):
    return _eval_db(collection, 'find', query)


def db_save(collection, data):
    return _eval_db(collection, 'insert', data, check_keys=False)


def db_find_one(collection, query):
    return _eval_db(collection, 'find_one', query)


def _eval_db(collection, method, *args, **kwargs):
    exec_collection = DB.__getattr__(collection)
    return exec_collection.__getattribute__(method)(*args, **kwargs)


def _eval_db_find_one(query, table=None):
    return _eval_db(table, 'find_one', query)
