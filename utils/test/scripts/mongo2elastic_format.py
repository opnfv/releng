#! /usr/bin/env python


def _convert_value(value):
    return value if value != '' else 0


def _convert_duration(duration):
    if (isinstance(duration, str) or isinstance(duration, unicode)) and ':' in duration:
        hours, minutes, seconds = duration.split(":")
        hours = _convert_value(hours)
        minutes = _convert_value(minutes)
        seconds = _convert_value(seconds)
        int_duration = 3600 * int(hours) + 60 * int(minutes) + float(seconds)
    else:
        int_duration = duration
    return int_duration


def format_normal(testcase):
    """
    Look for these and leave any of those:
        details.duration
        details.tests
        details.failures

    If none are present, then return False
    """
    found = False
    testcase_details = testcase['details']
    fields = ['duration', 'tests', 'failures']
    if isinstance(testcase_details, dict):
        for key, value in testcase_details.items():
            if key in fields:
                found = True
                if key == 'duration':
                    testcase_details[key] = _convert_duration(value)
            else:
                del testcase_details[key]

    if 'tests' in testcase_details and 'failures' in testcase_details:
        testcase_tests = float(testcase_details['tests'])
        testcase_failures = float(testcase_details['failures'])
        if testcase_tests != 0:
            testcase_details['success_percentage'] = 100 * (testcase_tests - testcase_failures) / testcase_tests
        else:
            testcase_details['success_percentage'] = 0


    return found


def format_rally(testcase):
    """
    Structure:
        details.[{summary.duration}]
        details.[{summary.nb success}]
        details.[{summary.nb tests}]

    Find data for these fields
        -> details.duration
        -> details.tests
        -> details.success_percentage
    """
    details = testcase['details']
    summary = None
    for item in details:
        if 'summary' in item:
            summary = item['summary']

    if not summary:
        return False

    testcase['details'] = {
        'duration': summary['duration'],
        'tests': summary['nb tests'],
        'success_percentage': summary['nb success']
    }
    return True


def _get_statistics(orig_data, stat_fields, stat_values=None):
    test_results = {}
    for stat_data in orig_data:
        for field in stat_fields:
            stat_value = stat_data[field]
            if stat_value in test_results:
                test_results[stat_value] += 1
            else:
                test_results[stat_value] = 1

    if stat_values is not None:
        for stat_value in stat_values:
            if stat_value not in test_results:
                test_results[stat_value] = 0

    return test_results


def format_onos(testcase):
    """
    Structure:
        details.FUNCvirNet.duration
        details.FUNCvirNet.status.[{Case result}]
        details.FUNCvirNetL3.duration
        details.FUNCvirNetL3.status.[{Case result}]

    Find data for these fields
        -> details.FUNCvirNet.duration
        -> details.FUNCvirNet.tests
        -> details.FUNCvirNet.failures
        -> details.FUNCvirNetL3.duration
        -> details.FUNCvirNetL3.tests
        -> details.FUNCvirNetL3.failures
    """
    testcase_details = testcase['details']

    if 'FUNCvirNet' not in testcase_details or 'FUNCvirNetL3' not in testcase_details:
        return False

    funcvirnet_details = testcase_details['FUNCvirNet']['status']
    funcvirnet_stats = _get_statistics(funcvirnet_details, ('Case result',), ('PASS', 'FAIL'))
    funcvirnet_passed = funcvirnet_stats['PASS']
    funcvirnet_failed = funcvirnet_stats['FAIL']
    funcvirnet_all = funcvirnet_passed + funcvirnet_failed

    funcvirnetl3_details = testcase_details['FUNCvirNetL3']['status']
    funcvirnetl3_stats = _get_statistics(funcvirnetl3_details, ('Case result',), ('PASS', 'FAIL'))
    funcvirnetl3_passed = funcvirnetl3_stats['PASS']
    funcvirnetl3_failed = funcvirnetl3_stats['FAIL']
    funcvirnetl3_all = funcvirnetl3_passed + funcvirnetl3_failed

    testcase_details['FUNCvirNet'] = {
        'duration': _convert_duration(testcase_details['FUNCvirNet']['duration']),
        'tests': funcvirnet_all,
        'failures': funcvirnet_failed
    }
    testcase_details['FUNCvirNetL3'] = {
        'duration': _convert_duration(testcase_details['FUNCvirNetL3']['duration']),
        'tests': funcvirnetl3_all,
        'failures': funcvirnetl3_failed
    }
    return True


def format_vims(testcase):
    """
    Structure:
        details.sig_test.result.[{result}]
        details.sig_test.duration
        details.vIMS.duration
        details.orchestrator.duration

    Find data for these fields
        -> details.sig_test.duration
        -> details.sig_test.tests
        -> details.sig_test.failures
        -> details.sig_test.passed
        -> details.sig_test.skipped
        -> details.vIMS.duration
        -> details.orchestrator.duration
    """
    testcase_details = testcase['details']
    test_results = _get_statistics(testcase_details['sig_test']['result'],
                                   ('result',),
                                   ('Passed', 'Skipped', 'Failed'))
    passed = test_results['Passed']
    skipped = test_results['Skipped']
    failures = test_results['Failed']
    all_tests = passed + skipped + failures
    testcase['details'] = {
        'sig_test': {
            'duration': testcase_details['sig_test']['duration'],
            'tests': all_tests,
            'failures': failures,
            'passed': passed,
            'skipped': skipped
        },
        'vIMS': {
            'duration': testcase_details['vIMS']['duration']
        },
        'orchestrator': {
            'duration': testcase_details['orchestrator']['duration']
        }
    }
    return True
