from setuptools import setup, find_packages

setup(
  name='opnfv-artifacts',
  version='0.1.0',
  description='Generates an HTMLDir site from a Google Storage bucket',
  author="Trevor Bramwell",
  author_email="tbramwell@linuxfoundation.org",
  url='https://gerrit.opnfv.org/gerrit/releng',
  packages=find_packages(),
  package_data={
    'artifacts': [
      'templates/*',
      'defaults.cfg',
    ],
  },
  install_requires=[
    'jinja2',
    'google-cloud-storage',
  ],
  entry_points={
    'console_scripts': [
      'opnfv-artifacts=artifacts.generate:main',
    ]
  },
)
