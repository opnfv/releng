__author__ = 'serena'

import setuptools

try:
    import multiprocessing
except ImportError:
    pass

setuptools.setup(
    setup_requires=['pbr>=1.8'],
    pbr=True)
