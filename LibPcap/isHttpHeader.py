__author__ = 'michal'


def is_http_header(txt):
    return txt.startswith('HTTP') or txt.startswith('GET') or txt.startswith('POST')