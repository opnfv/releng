import yaml


with open('./testcases.yaml') as f:
    testcases_yaml = yaml.safe_load(f)
f.close()


def get_format(project, case):
    testcases = testcases_yaml.get(project)
    if isinstance(testcases, list):
        for case_dict in testcases:
            if case_dict['name'] == case:
                return 'format_' + case_dict['format'].strip()
    return None


if __name__ == '__main__':
    fmt = get_format('functest', 'vping_ssh')
    print fmt