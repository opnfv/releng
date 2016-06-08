##############################################################################
# Copyright (c) 2016 ZTE Corporation
# feng.xiaowei@zte.com.cn
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import subprocess

possible_processes = [
    'result_collection_api',
    'opnfv-testapi'
]


def kill_olds():
    for proc in possible_processes:
        query = 'ps -ef | grep {} | grep -v grep'.format(proc)
        runnings = execute_with_output(query)
        if runnings:
            for running in runnings:
                kill = 'kill -kill ' + running.split()[1]
                execute_with_output(kill)
            runnings = execute_with_output(query)
        assert len(runnings) == 0, 'kill %s failed'.format(proc)


def install_dependencies():
    execute_with_assert('pip install -r ../requirements.txt')


def install_new():
    execute_with_assert('cd ../ && python setup.py install')


def run_new():
    execute_with_assert('opnfv-testapi &')


def execute_with_output(cmd):
    return subprocess.Popen(cmd, shell=True,
                            stdout=subprocess.PIPE).stdout.readlines()


def execute_with_assert(cmd):
    execute_output = subprocess.call(cmd, shell=True)
    assert execute_output == 0


if __name__ == '__main__':
    kill_olds()
    install_dependencies()
    install_new()
    run_new()
