__author__ = 'michal'

import re


class MyPasswordFinder:
    def __init__(self):
        self.kwrd = 'pass|secret'
        self.hend = '([^\n]+\n)'

    def find_pass(self, http):
        """
        when dict given as http, the dict should be {'header':'...', 'body': '...'}
        when str given as http, the string should contain header with data
        :param http: (dict|str)
        :return:
        """
        if type(http) is str:

            return self.find_pass_in_http_message(http)

        elif type(http) is dict:

            return self.find_pass_parsed_header(http)

    def find_pass_in_http_message(self, http_raw):
        # 'POST.*(\r\n){2}email=([^\r\n&]*)

        http_raw = http_raw.replace(u'\r\n', u'\n')
        print http_raw

        r = {
            # Find a line in POST method which can contain pass
            'POST_pass': 'POST\s*(?P<addr>[^\n]*)(' + self.hend + '){0,16}\n(?P<pass>[^\n]*(' + self.kwrd + ')[^\n]*)'
        }
        m = re.search(r.get('POST_pass'), http_raw, re.MULTILINE | re.DOTALL)
        result = m.groupdict() if m is not None else None
        return result

    def find_pass_parsed_header(self, http_data):

        # 'email=geabaeph%40dodsi.com&passwd=asdfasdfasdf&SubmitLogin=Zaloguj

        pass_rex = '^(?P<pass>.*(' + self.kwrd + ').*)$'
        addr_rex = '^[^\s]* (?P<addr>[^\s]*) [^\s]*$'

        pass_match = re.search(pass_rex, http_data['data'], re.MULTILINE)
        addr_match = re.search(addr_rex, http_data['request_line'], re.MULTILINE)

        pass_grdic = pass_match.groupdict() if pass_match is not None else None
        addr_grdic = addr_match.groupdict() if addr_match is not None else None

        result = None

        if pass_grdic is not None and addr_grdic is not None:
            url = (http_data['fields']['Host'] if 'Host' in http_data['fields'] else '') + addr_grdic['addr']
            result = {'pass': pass_grdic['pass'], 'addr': url}

        return result
