#!/usr/bin/python
#
# This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
import re


class TestCase(object):

    def __init__(self, name, project, constraints,
                 criteria=-1, isRunnable=True, tier=-1):
        self.name = name
        self.project = project
        self.constraints = constraints
        self.criteria = criteria
        self.isRunnable = isRunnable
        self.tier = tier
        display_name_matrix = {'healthcheck': 'healthcheck',
                               'vping_ssh': 'vPing (ssh)',
                               'vping_userdata': 'vPing (userdata)',
                               'odl': 'ODL',
                               'onos': 'ONOS',
                               'ocl': 'OCL',
                               'tempest_smoke_serial': 'Tempest (smoke)',
                               'tempest_full_parallel': 'Tempest (full)',
                               'tempest_defcore': 'Tempest (Defcore)',
                               'refstack_defcore': 'Refstack',
                               'rally_sanity': 'Rally (smoke)',
                               'bgpvpn': 'bgpvpn',
                               'rally_full': 'Rally (full)',
                               'vims': 'vIMS',
                               'doctor-notification': 'Doctor',
                               'promise': 'Promise',
                               'moon': 'Moon',
                               'copper': 'Copper',
                               'security_scan': 'Security',
                               'multisite': 'Multisite',
                               'domino-multinode': 'Domino',
                               'functest-odl-sfc': 'SFC',
                               'onos_sfc': 'SFC',
                               'parser-basics': 'Parser',
                               'connection_check': 'Health (connection)',
                               'api_check': 'Health (api)',
                               'snaps_smoke': 'SNAPS',
                               'snaps_health_check': 'Health (dhcp)',
                               'gluon_vping': 'Netready',
                               'fds': 'FDS',
                               'cloudify_ims': 'vIMS (Cloudify)',
                               'orchestra_ims': 'OpenIMS (OpenBaton)',
                               'opera_ims': 'vIMS (Open-O)',
                               'vyos_vrouter': 'vyos',
                               'barometercollectd': 'Barometer',
                               'odl_netvirt': 'Netvirt',
                               'security_scan': 'Security'}
        try:
            self.displayName = display_name_matrix[self.name]
        except:
            self.displayName = "unknown"

    def getName(self):
        return self.name

    def getProject(self):
        return self.project

    def getConstraints(self):
        return self.constraints

    def getCriteria(self):
        return self.criteria

    def getTier(self):
        return self.tier

    def setCriteria(self, criteria):
        self.criteria = criteria

    def setIsRunnable(self, isRunnable):
        self.isRunnable = isRunnable

    def checkRunnable(self, installer, scenario, config):
        # Re-use Functest declaration
        # Retrieve Functest configuration file functest_config.yaml
        is_runnable = True
        config_test = config
        # print " *********************** "
        # print TEST_ENV
        # print " ---------------------- "
        # print "case = " + self.name
        # print "installer = " + installer
        # print "scenario = " + scenario
        # print "project = " + self.project

        # Retrieve test constraints
        # Retrieve test execution param
        test_execution_context = {"installer": installer,
                                  "scenario": scenario}

        # By default we assume that all the tests are always runnable...
        # if test_env not empty => dependencies to be checked
        if config_test is not None and len(config_test) > 0:
            # possible criteria = ["installer", "scenario"]
            # consider test criteria from config file
            # compare towards CI env through CI en variable
            for criteria in config_test:
                if re.search(config_test[criteria],
                             test_execution_context[criteria]) is None:
                    # print "Test "+ test + " cannot be run on the environment"
                    is_runnable = False
        # print is_runnable
        self.isRunnable = is_runnable

    def toString(self):
        testcase = ("Name=" + self.name + ";Criteria=" +
                    str(self.criteria) + ";Project=" + self.project +
                    ";Constraints=" + str(self.constraints) +
                    ";IsRunnable" + str(self.isRunnable))
        return testcase

    def getDisplayName(self):
        return self.displayName
