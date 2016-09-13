import json

import urllib3

http = urllib3.PoolManager()


def delete_request(url, creds, body=None):
    headers = urllib3.make_headers(basic_auth=creds)
    http.request('DELETE', url, headers=headers, body=body)


def publish_json(json_ojb, creds, output_destination):
    json_dump = json.dumps(json_ojb)
    if output_destination == 'stdout':
        print json_dump
        return 200, None
    else:
        headers = urllib3.make_headers(basic_auth=creds)
        result = http.request('POST', output_destination, headers=headers, body=json_dump)
        return result.status, result.data


def _get_nr_of_hits(elastic_json):
    return elastic_json['hits']['total']


def get_elastic_docs(elastic_url, creds, days):
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

    # 1. get the number of results
    headers = urllib3.make_headers(basic_auth=creds)
    elastic_json = json.loads(http.request('GET', elastic_url + '/_search?size=0', headers=headers, body=body).data)
    print elastic_json
    nr_of_hits = _get_nr_of_hits(elastic_json)

    # 2. get all results
    elastic_json = json.loads(http.request('GET', elastic_url + '/_search?size={}'.format(nr_of_hits), headers=headers, body=body).data)

    elastic_docs = []
    for hit in elastic_json['hits']['hits']:
        elastic_docs.append(hit['_source'])
    return elastic_docs
