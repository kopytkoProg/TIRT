from dpkt.asn1 import INTEGER

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
            self.hs[ports] = {
                'data': data,
                'type': None,
                'length': None,
                'time': current_milli_time(),
                'chunkInProgress': None
            }
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
                            # print '-1 == header.find'
                            self.hs[k]['length'] = len(header) + 4
                        elif -1 != header.find('Transfer-Encoding: chunked'):
                            # Transfer-Encoding:
                            print '-1 != header.find'
                            self.hs[k]['length'] = len(header) + 4
                            self.hs[k]['chunkInProgress'] = True
                        else:
                            # header don't have Content-Length field
                            self.hs.pop(k)

            # handle chunked Transfer
            only_chunked = [e for e in self.hs.keys() if self.hs[e]['chunkInProgress'] is True]

            for k in only_chunked:

                # if in previous loop was any length field incrementation
                any_chunk_changes = True

                while any_chunk_changes:
                    any_chunk_changes = False

                    start_of_chunk_length = self.hs[k]['length']  # = self.hs[k]['data'].find('\r\n\r\n') + 4

                    # if received mor data then length
                    if start_of_chunk_length < len(self.hs[k]['data']):

                        # find eol wher the chunk length is
                        end_of_chunk_length = self.hs[k]['data'][start_of_chunk_length:].find(
                            '\r\n') + start_of_chunk_length

                        # if chunk length found
                        if end_of_chunk_length != -1:

                            # try pars
                            try:
                                chunk_length_str = self.hs[k]['data'][start_of_chunk_length:end_of_chunk_length]
                                chunk_length = int(chunk_length_str, base=16)
                            except Exception as e:
                                # if error then remove the stream from list

                                self.hs.pop(k)
                            else:

                                self.hs[k]['length'] += len(chunk_length_str) + 2 + 2 + chunk_length

                                if chunk_length == 0 and len(self.hs[k]['data']) == self.hs[k]['length']:
                                    result.append(self.hs.pop(k)['data'])

                                elif chunk_length == 0 and len(self.hs[k]['data']) > self.hs[k]['length']:
                                    d = self.hs[k]['data']
                                    l = self.hs[k]['length']
                                    self.hs.pop(k)

                                    result.append(d[:l])
                                    result.extend(self.add_packet(ports, d[l:]))

                                else:
                                    any_chunk_changes = True

            # add proper stream to response
            only_not_chunked = [e for e in self.hs.keys() if self.hs[e]['chunkInProgress'] is None]

            for k in only_not_chunked:
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
    http_1 = 'POST /rtvforum/login.php HTTP/1.1\r\nHost: www.elektroda.pl\r\nUser-Agent: xxxxxxxxxxxxxxxxxx/5.0 (Windows NT 6.3; WOW64; rv:37.0) Gecko/20100101 Firefox/37.0\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\nAccept-Language: pl,en-US;q=0.7,en;q=0.3\r\nAccept-Encoding: gzip, deflate\r\nReferer: http://www.elektroda.pl/rtvforum/index.php\r\nConnection: keep-alive\r\nContent-Type: application/x-w'
    http_2 = 'ww-form-urlencoded\r\nContent-Length: 46\r\n\r\nusername=Zaaa'
    http_3 = 'aap&password=kura10&login=ZalogujPOST\r\nContent-Length: 5\r\n\r\n12345'
    # print r.add_packet((1, 2), http_1)
    # print r.add_packet((1, 2), http_2)
    # print r.add_packet((1, 2), http_3)


    http_12 = 'POST\r\nContent-Length: 5\r\n\r\n12345POST /rtvforum/login.php HTTP/1.1\r\nHost: www.elektroda.pl\r\nUser-Agent: Mozilla/5.0 (Windows NT 6.3; WOW64; rv:37.0) Gecko/20100101 Firefox/37.0\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\nAccept-Language: pl,en-US;q=0.7,en;q=0.3\r\nAccept-Encoding: gzip, deflate\r\nReferer: http://www.elektroda.pl/rtvforum/index.php\r\nConnection: keep-alive\r\nContent-Type: application/x-w'
    http_22 = 'ww-form-urlencoded\r\n'
    http_32 = 'Transfer-Encoding: chunked\r\n\r\n5\r\n12345\r\n0\r\n\r\nPOST\r\nContent-Length: 5\r\n\r\n12345'
    # print r.add_packet((1, 2), http_12)
    # print r.add_packet((1, 2), http_22)
    # print r.add_packet((1, 2), http_32)

    with open('chunkedFullExample.txt', 'rb') as content_file:
        # print {'x':content_file.read()}
        print r.add_packet((1, 2), content_file.read())

