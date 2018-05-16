##############################################################################
# Copyright (c) 2016 Tim Rozet (trozet@redhat.com) and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import pprint
import yaml
from jinja2 import Environment
from jinja2 import FileSystemLoader


def render_jjb():
    """Render JJB output from scenarios.yaml.hidden file and jinja
    template"""

    gspathname = dict()
    branch = dict()
    build_slave = dict()
    env = Environment(loader=FileSystemLoader('./'), autoescape=True)

    with open('scenarios.yaml.hidden') as _:
        scenarios = yaml.safe_load(_)

    template = env.get_template('apex.yaml.j2')

    print("Scenarios are: ")
    pprint.pprint(scenarios)

    for stream in scenarios:
        if stream == 'master':
            gspathname['master'] = ''
            branch[stream] = stream
        else:
            gspathname[stream] = '/' + stream
            branch[stream] = 'stable/' + stream
        build_slave[stream] = 'apex-baremetal-{}'.format(stream)

    output = template.render(scenarios=scenarios, gspathname=gspathname,
                             branch=branch, build_slave=build_slave)

    with open('./apex.yaml', 'w') as fh:
        fh.write(output)

if __name__ == "__main__":
    render_jjb()
