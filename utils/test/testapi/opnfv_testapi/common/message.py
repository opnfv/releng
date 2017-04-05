not_found_base = 'Could Not Found'
exist_base = 'Already Exists'


def no_body():
    return 'No Body'


def not_found(key, value):
    return '{} {} [{}]'.format(not_found_base, key, value)


def missing(name):
    return '{} Missing'.format(name)


def exist(key, value):
    return '{} [{}] {}'.format(key, value, exist_base)


def bad_format(error):
    return 'Bad Format [{}]'.format(error)


def unauthorized():
    return 'No Authentication Header'


def invalid_token():
    return 'Invalid Token'


def no_update():
    return 'Nothing to update'


def must_int(name):
    return '{} must be int'.format(name)
