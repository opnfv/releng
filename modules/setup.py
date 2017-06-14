##############################################################################
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################


from setuptools import setup, find_packages


setup(
    name="opnfv",
    version="danube",
    packages=find_packages(),
    include_package_data=True,
    package_data={
    },
    url="https://www.opnfv.org",
    install_requires=["paramiko>=2.0",
                      "mock>=2.0",
                      "requests!=2.12.2,>=2.10.0"],
    test_requires=["nose",
                   "coverage>=4.0"]
)
