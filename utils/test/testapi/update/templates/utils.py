##############################################################################
# Copyright (c) 2016 ZTE Corporation
# feng.xiaowei@zte.com.cn
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import os
import urlparse
import subprocess


def get_abspath(path):
    assert os.path.isdir(path), 'Path %s can\'t be found.' % path
    return os.path.abspath(path)


def parse_mongodb_url(url):
    url = urlparse.urlparse(url)
    assert url.scheme == 'mongodb', 'URL must be a MongoDB URL'
    return url


def url_parse(url):
    url = parse_mongodb_url(url)
    return url.username, url.password, url.hostname, url.port


def execute(cmd, args):
    (username, password, hostname, port) = url_parse(args.url)
    cmd.extend(['--host', '%s' % hostname, '--port', '%s' % port])
    db = args.db
    if db is not None:
        cmd.extend(['--db', '%s' % db])
    if username is not None:
        cmd.extend(['-u', '%s' % username, '-p', '%s' % password])
    print('execute: %s' % cmd)
    execute_output = subprocess.check_output(cmd)
    print(execute_output)


def main(method, parser):
    args = parser.parse_args()
    try:
        method(args)
    except AssertionError as msg:
        print(msg)
