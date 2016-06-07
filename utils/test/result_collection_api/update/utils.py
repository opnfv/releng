import os
import argparse
import logging
import datetime
import urlparse
import subprocess


def url_parse(url):
    url = urlparse.urlparse(url)
    assert url.scheme == 'mongodb', 'URL must be a MongoDB URL'

    return url.username, url.password, url.hostname, url.port


def execute(cmd, args):
    (username, password, hostname, port) = url_parse(args.url)
    cmd.extend(['--host', '%s' % hostname, '--port', '%s' % port])
    db = args.db
    if db is not None:
        cmd.extend(['--db', '%s' % db])
    if username is not None:
        cmd.extend(['-u', '%s' % username, '-p', '%s' % password])
    logging.info('execute: %s' % cmd)
    execute_output = subprocess.check_output(cmd)
    logging.info(execute_output)


def main(method, parser):
    args = parser.parse_args()
    try:
        method(args)
    except AssertionError, msg:
        logging.error(msg)
