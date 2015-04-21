__author__ = 'michal'

import re


class MyPasswordFinder:
    def __init__(self):
        pass

    def find_pass(self, http_raw):
        # 'POST.*(\r\n){2}email=([^\r\n&]*)

        key_words = 'pass|secret'
        header_line = '([^\n]+\n)'

        r = {
            # Find a line in POST method which can contain pass
            'POST_pass': 'POST\s*(?P<addr>[^\n]*)(' + header_line + '){0,16}\n(?P<pass>[^\n]*(' + key_words + ')[^\n]*)'
        }
        m = re.search(r.get('POST_pass'), http_raw, re.MULTILINE | re.DOTALL)
        result = m.groupdict() if m is not None else None
        return result



