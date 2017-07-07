##############################################################################
# Copyright (c) 2016 ZTE Corporation
# feng.xiaowei@zte.com.cn
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import argparse
import datetime
import os

from utils import execute, main, get_abspath

parser = argparse.ArgumentParser(description='Backup MongoDBs')

parser.add_argument('-u', '--url',
                    type=str,
                    required=False,
                    default='mongodb://127.0.0.1:27017/',
                    help='Mongo DB URL for Backups')
parser.add_argument('-o', '--output_dir',
                    type=str,
                    required=False,
                    default='./',
                    help='Output directory for the backup.')

parser.add_argument('-d', '--db',
                    type=str,
                    required=False,
                    default='test_results_collection',
                    help='database for the backup.')


def backup(args):
    db = args.db
    out = get_abspath(args.output_dir)
    now = datetime.datetime.now()
    out = os.path.join(out, '%s__%s' % (db, now.strftime('%Y_%m_%d_%H%M%S')))
    cmd = ['mongodump', '-o', '%s' % out]
    execute(cmd, args)


if __name__ == '__main__':
    main(backup, parser)
