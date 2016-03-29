#! /usr/bin/env python
import logging
import argparse
import shared_utils
import json
import urlparse

logger = logging.getLogger('clear_kibana')
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('/var/log/{}.log'.format(__name__))
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
logger.addHandler(file_handler)


def delete_all(url, es_user, es_passwd):
    ids = shared_utils.get_elastic_data(url, es_user, es_passwd, body=None, field='_id')
    for id in ids:
        del_url = '/'.join([url, id])
        shared_utils.delete_request(del_url, es_user, es_passwd)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Delete saved kibana searches, visualizations and dashboards')
    parser.add_argument('-e', '--elasticsearch-url', default='http://localhost:9200',
                        help='the url of elasticsearch, defaults to http://localhost:9200')

    parser.add_argument('-u', '--elasticsearch-username',
                        help='the username for elasticsearch')

    parser.add_argument('-p', '--elasticsearch-password',
                        help='the password for elasticsearch')

    args = parser.parse_args()
    base_elastic_url = args.elasticsearch_url
    es_user = args.elasticsearch_username
    es_passwd = args.elasticsearch_password

    urls = (urlparse.urljoin(base_elastic_url, '/.kibana/visualization'),
            urlparse.urljoin(base_elastic_url, '/.kibana/dashboard'),
            urlparse.urljoin(base_elastic_url, '/.kibana/search'))

    for url in urls:
        delete_all(url, es_user, es_passwd)
