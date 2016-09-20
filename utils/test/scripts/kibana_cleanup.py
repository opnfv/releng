#! /usr/bin/env python
import logging
import urlparse

import argparse

import shared_utils

logger = logging.getLogger('clear_kibana')
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('/var/log/{}.log'.format('clear_kibana'))
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
logger.addHandler(file_handler)


def delete_all(url, es_creds):
    ids = shared_utils.get_elastic_docs(url, es_creds, body=None, field='_id')
    for id in ids:
        del_url = '/'.join([url, id])
        shared_utils.delete_request(del_url, es_creds)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Delete saved kibana searches, visualizations and dashboards')
    parser.add_argument('-e', '--elasticsearch-url', default='http://localhost:9200',
                        help='the url of elasticsearch, defaults to http://localhost:9200')

    parser.add_argument('-u', '--elasticsearch-username', default=None,
                        help='The username with password for elasticsearch in format username:password')

    args = parser.parse_args()
    base_elastic_url = args.elasticsearch_url
    es_creds = args.elasticsearch_username

    urls = (urlparse.urljoin(base_elastic_url, '/.kibana/visualization'),
            urlparse.urljoin(base_elastic_url, '/.kibana/dashboard'),
            urlparse.urljoin(base_elastic_url, '/.kibana/search'))

    for url in urls:
        delete_all(url, es_creds)

