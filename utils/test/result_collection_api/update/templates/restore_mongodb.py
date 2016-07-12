##############################################################################
# Copyright (c) 2016 ZTE Corporation
# feng.xiaowei@zte.com.cn
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import argparse

from utils import execute, main, get_abspath

parser = argparse.ArgumentParser(description='Restore MongoDBs')

parser.add_argument('-u', '--url',
                    type=str,
                    required=False,
                    default='mongodb://127.0.0.1:27017/',
                    help='Mongo DB URL for Backup')
parser.add_argument('-i', '--input_dir',
                    type=str,
                    required=True,
                    help='Input directory for the Restore.')
parser.add_argument('-d', '--db',
                    type=str,
                    required=False,
                    default='test_results_collection',
                    help='database name after the restore.')


def restore(args):
    input_dir = get_abspath(args.input_dir)
    cmd = ['mongorestore', '%s' % input_dir]
    execute(cmd, args)


if __name__ == '__main__':
    main(restore, parser)
