

no_body = lambda: 'No Body'
not_found_base = 'Could Not Found'
not_found = lambda key, value: '{} {} [{}]'.format(not_found_base, key, value)
missing = lambda name: '{} Missing'.format(name)
exist_base = 'Already Exists'
exist = lambda key, value: '{} [{}] {}'.format(key, value, exist_base)
