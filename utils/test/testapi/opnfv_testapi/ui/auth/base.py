import random
import string

from six.moves.urllib import parse

from opnfv_testapi.resources import handlers


class BaseHandler(handlers.GenericApiHandler):
    def __init__(self, application, request, **kwargs):
        super(BaseHandler, self).__init__(application, request, **kwargs)
        self.table = 'users'

    def set_cookies(self, cookies):
        for cookie_n, cookie_v in cookies:
            self.set_secure_cookie(cookie_n, cookie_v)


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
