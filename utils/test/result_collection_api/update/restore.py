import os
import argparse
import logging

from utils import execute, main

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser(description='Restore MongoDBs')

parser.add_argument('-u', '--url',
                    type=str,
                    required=False,
                    default='mongodb://127.0.0.1:27017/',
                    help='Mongo DB URL for Backup')
parser.add_argument('-i', '--input_dir',
                    type=str,
                    required=False,
                    default='./',
                    help='Input directory for the Restore.')
parser.add_argument('-d', '--db',
                    type=str,
                    required=False,
                    default=None,
                    help='database for the restore.')


def restore(args):
    input_dir = args.input_dir
    assert os.path.isdir(input_dir), 'Directory %s can\'t be found.' % input_dir
    cmd = ['mongorestore', '%s' % input_dir]
    execute(cmd, args)


if __name__ == '__main__':
    main(restore, parser)
