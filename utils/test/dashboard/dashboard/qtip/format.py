#! /usr/bin/env python


def format_qpi(testcase):
    """
    Look for these and leave any of those:
        details.index

    If none are present, then return False
    """
    details = testcase['details']
    if 'index' not in details:
        return False

    for key, value in details.items():
        if key != 'index':
            del details[key]

    return True
