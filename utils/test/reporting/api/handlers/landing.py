##############################################################################
# Copyright (c) 2016 Huawei Technologies Co.,Ltd and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import requests

from tornado.escape import json_encode
from tornado.escape import json_decode

from api.handlers import BaseHandler
from api import conf


class FiltersHandler(BaseHandler):
    def get(self):
        self._set_header()

        filters = {
            'filters': {
                'status': ['success', 'warning', 'danger'],
                'projects': ['functest', 'yardstick'],
                'installers': ['apex', 'compass', 'fuel', 'joid'],
                'version': ['colorado', 'master'],
                'loops': ['daily', 'weekly', 'monthly'],
                'time': ['10 days', '30 days']
            }
        }
        return self.write(json_encode(filters))


class ScenariosHandler(BaseHandler):
    def post(self):
        self._set_header()

        body = json_decode(self.request.body)
        args = self._get_args(body)

        scenarios = self._get_result_data(self._get_scenarios(), args)

        return self.write(json_encode(dict(scenarios=scenarios)))

    def _get_result_data(self, data, args):
        data = self._filter_status(data, args)
        return {s: self._get_scenario_result(s, data[s], args) for s in data}

    def _filter_status(self, data, args):
        return {k: v for k, v in data.items() if v['status'] in args['status']}

    def _get_scenario_result(self, scenario, data, args):
        result = {
            'status': data.get('status'),
            'installers': self._get_installers_result(data['installers'], args)
        }
        return result

    def _get_installers_result(self, data, args):
        func = self._get_installer_result
        return {k: func(k, data.get(k, {}), args) for k in args['installers']}

    def _get_installer_result(self, installer, data, args):
        projects = data.get(args['version'], [])
        return [self._get_project_data(projects, p) for p in args['projects']]

    def _get_project_data(self, projects, project):
        atom = {
            'project': project,
            'score': None,
            'status': None
        }
        for p in projects:
            if p['project'] == project:
                return p
        return atom

    def _get_scenarios(self):
        url = '{}/scenarios'.format(conf.base_url)
        resp = requests.get(url).json()
        data = self._change_to_utf8(resp).get('scenarios', {})
        return {a.get('name'): self._get_scenario(a.get('installers', [])
                                                  ) for a in data}

    def _get_scenario(self, data):
        installers = {a.get('installer'): self._get_installer(a.get('versions',
                                                                    [])
                                                              ) for a in data}
        scenario = {
            'status': self._get_status(),
            'installers': installers
        }
        return scenario

    def _get_status(self):
        return 'success'

    def _get_installer(self, data):
        return {a.get('version'): self._get_version(a) for a in data}

    def _get_version(self, data):
        try:
            scores = data.get('score', {}).get('projects')[0]
            trusts = data.get('trust_indicator', {}).get('projects')[0]
        except (TypeError, IndexError):
            return []
        else:
            scores = {key: [dict(date=a.get('date')[:10],
                                 score=a.get('score')
                                 ) for a in scores[key]] for key in scores}
            trusts = {key: [dict(date=a.get('date')[:10],
                                 status=a.get('status')
                                 ) for a in trusts[key]] for key in trusts}
            atom = self._get_atom(scores, trusts)
            return [dict(project=k,
                         score=sorted(atom[k], reverse=True)[0].get('score'),
                         status=sorted(atom[k], reverse=True)[0].get('status')
                         ) for k in atom if atom[k]]

    def _get_atom(self, scores, trusts):
        s = {k: {a['date']: a['score'] for a in scores[k]} for k in scores}
        t = {k: {a['date']: a['status'] for a in trusts[k]} for k in trusts}
        return {k: [dict(score=s[k][a], status=t[k][a], data=a
                         ) for a in s[k] if a in t[k]] for k in s}

    def _change_to_utf8(self, obj):
        if isinstance(obj, dict):
            return {str(k): self._change_to_utf8(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._change_to_utf8(ele) for ele in obj]
        else:
            try:
                new = eval(obj)
                if isinstance(new, int):
                    return obj
                return self._change_to_utf8(new)
            except (NameError, TypeError, SyntaxError):
                return str(obj)

    def _get_args(self, body):
        status = self._get_status_args(body)
        projects = self._get_projects_args(body)
        installers = self._get_installers_args(body)

        args = {
            'status': status,
            'projects': projects,
            'installers': installers,
            'version': body.get('version', 'master').lower(),
            'loops': body.get('loops', 'daily').lower(),
            'time': body.get('times', '10 days')[:2].lower()
        }
        return args

    def _get_status_args(self, body):
        status_all = ['success', 'warning', 'danger']
        status = [a.lower() for a in body.get('status', ['all'])]
        return status_all if 'all' in status else status

    def _get_projects_args(self, body):
        project_all = ['functest', 'yardstick']
        projects = [a.lower() for a in body.get('projects', ['all'])]
        return project_all if 'all' in projects else projects

    def _get_installers_args(self, body):
        installer_all = ['apex', 'compass', 'fuel', 'joid']
        installers = [a.lower() for a in body.get('installers', ['all'])]
        return installer_all if 'all' in installers else installers
