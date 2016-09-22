import yaml


with open('./functest/testcases.yaml') as f:
    testcases_yaml = yaml.safe_load(f)
f.close()


def compose_format(fmt):
    return 'format_' + fmt.strip()


def get_format(project, case):
    testcases = testcases_yaml.get(project)
    if isinstance(testcases, list):
        for case_dict in testcases:
            if case_dict['name'] == case:
                return compose_format(case_dict['format'])
    return None


if __name__ == '__main__':
    fmt = get_format('functest', 'vping_ssh')
    print fmt
