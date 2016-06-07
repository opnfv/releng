import os
import argparse
import logging
import datetime

from utils import execute, main

logging.basicConfig(level=logging.INFO)

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
    output_dir = args.output_dir
    assert os.path.isdir(output_dir), 'Directory %s can\'t be found.' % output_dir

    now = datetime.datetime.now()
    output_dir = os.path.abspath(
        os.path.join(output_dir,
                     '%s__%s' % (db, now.strftime('%Y_%m_%d_%H%M%S')))
    )
    cmd = ['mongodump', '-o', '%s' % output_dir]
    execute(cmd, args)

if __name__ == '__main__':
    main(backup, parser)
