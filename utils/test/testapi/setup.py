import os
import subprocess

import setuptools

__author__ = 'serena'

try:
    import multiprocessing  # noqa
except ImportError:
    pass

dirpath = os.path.dirname(os.path.abspath(__file__))
subprocess.call(['ln', '-s',
                 '{}/3rd_party/static'.format(dirpath),
                 '{}/opnfv_testapi/static'.format(dirpath)])

setuptools.setup(
    setup_requires=['pbr==2.0.0'],
    pbr=True)
