import urllib3
import json
http = urllib3.PoolManager()


def delete_request(url, username, password, body=None):
    headers = urllib3.util.make_headers(basic_auth=':'.join([username, password]))
    http.request('DELETE', url, headers=headers, body=body)


def publish_json(json_ojb, username, password, output_destination):
    json_dump = json.dumps(json_ojb)
    if output_destination == 'stdout':
        print json_dump
        return 200, None
    else:
        headers = urllib3.util.make_headers(basic_auth=':'.join([username, password]))
        result = http.request('POST', output_destination, headers=headers, body=json_dump)
        return result.status, result.data


def _get_nr_of_hits(elastic_json):
    return elastic_json['hits']['total']


def get_elastic_data(elastic_url, username, password, body, field='_source'):
    # 1. get the number of results
    headers = urllib3.util.make_headers(basic_auth=':'.join([username, password]))
    elastic_json = json.loads(http.request('GET', elastic_url + '/_search?size=0', headers=headers, body=body).data)
    nr_of_hits = _get_nr_of_hits(elastic_json)

    # 2. get all results
    elastic_json = json.loads(http.request('GET', elastic_url + '/_search?size={}'.format(nr_of_hits), headers=headers, body=body).data)

    elastic_data = []
    for hit in elastic_json['hits']['hits']:
        elastic_data.append(hit[field])
    return elastic_data
