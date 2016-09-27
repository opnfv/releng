import json

import urllib3

http = urllib3.PoolManager()


def _request(method, url, creds=None, body=None):
    headers = urllib3.make_headers(basic_auth=creds)
    return http.request(method, url, headers=headers, body=body)


def _post(url, creds=None, body=None):
    return _request('POST', url, creds=creds, body=body)


def _get(url, creds=None, body=None):
    return json.loads(_request('GET', url, creds=creds, body=body).data)


def delete_docs(url, creds=None, body=None):
    return _request('DELETE', url, creds=creds, body=body)


def publish_docs(docs, creds, to):
    json_docs = json.dumps(docs)
    if to == 'stdout':
        print json_docs
        return 200, None
    else:
        result = _post(to, creds=creds, body=json_docs)
        return result.status, result.data


def _get_docs_nr(url, creds=None, body=None):
    res_data = _get('{}/_search?size=0'.format(url), creds=creds, body=body)
    print type(res_data), res_data
    return res_data['hits']['total']


def get_docs(url, creds=None, body=None, field='_source'):

    docs_nr = _get_docs_nr(url, creds=creds, body=body)
    res_data = _get('{}/_search?size={}'.format(url, docs_nr),
                    creds=creds, body=body)

    docs = []
    for hit in res_data['hits']['hits']:
        docs.append(hit[field])
    return docs


def get_elastic_docs_by_days(elastic_url, creds, days):
    if days == 0:
        body = '''{
            "query": {
                "match_all": {}
            }
        }'''
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
    else:
        raise Exception('Update days must be non-negative')
    return get_docs(elastic_url, creds, body)
