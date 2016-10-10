import json

from jinja2 import Environment, PackageLoader

env = Environment(loader=PackageLoader('elastic2kibana', 'templates'))
env.filters['jsonify'] = json.dumps


def dumps(a_dict, items):
    for key in items:
        a_dict[key] = json.dumps(a_dict[key])


def dumps_2depth(a_dict, key1, key2):
    a_dict[key1][key2] = json.dumps(a_dict[key1][key2])
