
import re

def sizeConv(s, target_unit='Mo'):
    '''
    convert size into the targeted unit
    '''
    s = str(s)
    p = re.compile('(\d+)+\s*([^\s]*)')
    (size, unit) = p.findall(s)[0]
    size = int(size)
    if unit == 'Go':
        size *= 1024
    elif unit == 'To':
        size *= 1024 * 1024

    if target_unit == 'Go':
        div = 1024
    elif target_unit == 'To':
        div = 1024 * 1024
    else:
        div = 1
    return size // div

def sizeSum(sizes, target_unit='Mo'):
    '''
    sum of sizes
    '''
    r = 0
    for s in sizes:
        r += sizeConv(s, target_unit)
    return r

class FilterModule(object):
    '''
    custom jinja2 filters for working with size
    '''

    def filters(self):
        return {
            'sizeConv': sizeConv,
            'sizeSum': sizeSum
        }
