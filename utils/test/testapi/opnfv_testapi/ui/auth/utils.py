import random
import string

from six.moves.urllib import parse


def get_token(length=30):
    """Get random token."""
    return ''.join(random.choice(string.ascii_lowercase)
                   for i in range(length))


def set_query_params(url, params):
    """Set params in given query."""
    url_parts = parse.urlparse(url)
    url = parse.urlunparse((
        url_parts.scheme,
        url_parts.netloc,
        url_parts.path,
        url_parts.params,
        parse.urlencode(params),
        url_parts.fragment))
    return url
