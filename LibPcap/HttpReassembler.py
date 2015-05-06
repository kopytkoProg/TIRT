__author__ = 'michal'
from isHttpHeader import is_http_header
import re
import time

current_milli_time = lambda: int(round(time.time() * 1000))
time_threshold = 1000 * 100


class HttpReassembler:
    def __init__(self):
        self.hs = {}

    def add_packet(self, ports, data):

        result = []
        any_changes = True

        if is_http_header(data):

            # reject current data on selected port
            self.hs[ports] = {'data': data, 'type': None, 'length': None, 'time': current_milli_time()}
        elif ports in self.hs:
            # append data to session
            self.hs[ports]['data'] += data
            self.hs[ports]['time'] = current_milli_time()
        else:
            any_changes = False

        # remove old inactive http stream
        for k in self.hs.keys():
            if current_milli_time() - self.hs[k]['time'] > time_threshold:
                self.hs.pop(k)

        # prepare streams
        if any_changes:
            for k in self.hs.keys():
                # if length of data not set
                if self.hs[k]['length'] is None:
                    eoh = self.hs[k]['data'].find('\r\n\r\n')
                    # if whole header received
                    if eoh != -1:

                        header = self.hs[k]['data'][:eoh]
                        rex = 'Content-Length: (?P<length>[0-9]*)'
                        m = re.search(rex, header, re.IGNORECASE)
                        g = m.groupdict() if m is not None else None

                        if g is not None:
                            # if contain Content-Length field
                            self.hs[k]['length'] = int(g['length']) + len(header) + 4
                        elif -1 == header.find('Transfer-Encoding: '):
                            # no message body in http packet
                            self.hs[k]['length'] = len(header) + 4
                        else:
                            # header don't have Content-Length field
                            self.hs.pop(k)

            # add proper stream to response
            for k in self.hs.keys():
                if self.hs[k]['length'] is not None and self.hs[k]['length'] == len(self.hs[k]['data']):
                    result.append(self.hs.pop(k)['data'])
                elif self.hs[k]['length'] is not None and self.hs[k]['length'] < len(self.hs[k]['data']):

                    d = self.hs[k]['data']
                    l = self.hs[k]['length']
                    self.hs.pop(k)

                    result.append(d[:l])
                    result.extend(self.add_packet(ports, d[l:]))

        return result


if __name__ == "__main__":
    r = HttpReassembler()
    http_1 = 'POST /rtvforum/login.php HTTP/1.1\r\nHost: www.elektroda.pl\r\nUser-Agent: Mozilla/5.0 (Windows NT 6.3; WOW64; rv:37.0) Gecko/20100101 Firefox/37.0\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\nAccept-Language: pl,en-US;q=0.7,en;q=0.3\r\nAccept-Encoding: gzip, deflate\r\nReferer: http://www.elektroda.pl/rtvforum/index.php\r\nConnection: keep-alive\r\nContent-Type: application/x-w'
    http_2 = 'ww-form-urlencoded\r\nContent-Length: 46\r\n\r\nusername=Zaaa'
    http_3 = 'aap&password=kura10&login=ZalogujPOST\r\nContent-Length: 5\r\n\r\n12345'
    print r.add_packet((1, 2), http_1)
    print r.add_packet((1, 2), http_2)
    print r.add_packet((1, 2), http_3)
