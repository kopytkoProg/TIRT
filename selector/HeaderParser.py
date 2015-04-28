__author__ = 'michal'

import re


class HttpRequest:
    def __init__(self):
        self.fields = {}
        """
        Header fields
        :type: dict

        """
        self.request_line = ''
        self.method = ''


class HttpResponse:
    def __init__(self):
        self.fields = {}
        """
        Header fields
        :type: dict

        """
        self.status_line = ''


class HeaderParser:
    def __init__(self, header):
        # only interesting method
        self.request_method = {'GET', 'POST', 'PUT'}
        self.header = header

    def parse(self):
        h_lines = self.header.split('\r\n')

        first_line = h_lines[0]
        first_word = first_line[:first_line.find(' ')]

        fields_lines = h_lines[1:]

        h_dict = {}
        for l in fields_lines:
            colon = l.find(':')
            name = l[:colon]
            value = l[colon + 1:].strip()
            h_dict[name] = value

        # --------------------------------------------------------------------------------------------------------------

        if first_word in self.request_method:

            req = HttpRequest()
            req.fields = h_dict
            req.request_line = first_line
            req.method = first_word

            return req

        elif first_line.startswith('HTTP'):

            res = HttpResponse()
            res.fields = h_dict
            res.status_line = first_line

            return res

        else:

            return None

    @staticmethod
    def data_to_string(data):
        return ''.join(map(chr, data))


if __name__ == "__main__":
    msg = {
        u'header': u"HTTP/1.1 200 OK\r\nDate: Tue, 28 Apr 2015 08:58:10 GMT\r\nServer: Apache\r\nX-Powered-By: PHP/5.3.3-7+squeeze3\r\nCache-Control: no-cache, must-revalidate, post-check=0, pre-check=0\r\nExpires: Mon, 26 Jul 1997 05:00:00 GMT\r\nP3P: CP='NOI DSP COR CUR OUR NID NOR'\r\nVary: Accept-Encoding\r\nContent-Encoding: gzip\r\nContent-Length: 55\r\nConnection: close\r\nContent-Type: text/javascript",
        u'data': [31, 139, 8, 0, 0, 0, 0, 0, 0, 3, 211, 215, 87, 40, 46, 73, 44, 201, 76, 54, 178, 224, 226, 210, 215,
                  87, 72, 173, 200, 44, 81, 40, 41, 74, 172, 48, 40, 226, 42, 75, 44, 82, 200, 143, 247, 7, 0, 21, 64,
                  213, 231, 35, 0, 0, 0]}
    o = HeaderParser(msg.get('header')).parse()
    print o
