#!/usr/bin/env python

# Copyright (c) 2016 Orange and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
#
# This class defines Python OPNFV exceptions
#


class OPNFVException(Exception):
    def __call__(self, *args):
        return self.__class__(*(self.args + args))


# ************************************
# Generic
# ************************************
class OPNFVSUTNotReachable(OPNFVException):
    """Target System Under Test is not reachable"""
    pass


class OPNFVCiExecutionError(OPNFVException):
    """Error occurs during CI exection"""
    pass


class TestDashboardError(OPNFVException):
    """Impossible to report results to dashboard"""
    pass


class TestReportingError(OPNFVException):
    """Impossible to report results to reporting"""
    pass


# ************************************
# Exceptions related to test DB
# ************************************
class TestDbNotReachable(OPNFVException):
    """Test database is not reachable"""
    pass


class UnknownScenario(OPNFVException):
    """Test scenario is unknown"""
    pass


class UnknownPod(OPNFVException):
    """Test POD is unknown"""
    pass


class UnknownProject(OPNFVException):
    """Project is unknown"""
    pass


class UnknownTestCase(OPNFVException):
    """Test case is unknown"""
    pass


class UnknownVersion(OPNFVException):
    """Version is unknown"""
    pass


class UnknownInstaller(OPNFVException):
    """Installer is not supported"""
    pass


# *******************
# Test project errors
# *******************
class FunctestExecutionError(OPNFVException):
    """Internal Functest error"""
    pass


class YardstickExecutionError(OPNFVException):
    """Internal Yardstick error"""
    pass


# **********************************
# Errors related to Feature projects
# **********************************
class TestCaseNotRunnable(OPNFVException):
    """test case incompatible with SUT, scenario, installer"""
    pass


class FeatureTestIntegrationError(OPNFVException):
    """Impossible to integrate Feature test"""
    pass


class FeatureTestExecutionError(OPNFVException):
    """Error during Feature test execution"""
    pass


# *********************************
# Errors related to VNF on boarding
# *********************************
class VNFTestNotRunnable(OPNFVException):
    """VNF test is not compatible with SUT, scenario, installer"""
    pass


class VNFIntegrationError(OPNFVException):
    """Impossible to integrate the VNF test"""
    pass


class VNFExecutionError(OPNFVException):
    """Error during VNF test execution"""
    pass
