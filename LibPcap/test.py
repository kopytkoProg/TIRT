#!/usr/bin/env python

import dpkt

f = open('myPass.cap', 'rb')
pcap = dpkt.pcap.Reader(f)

for ts, buf in pcap:
    print(buf)
    eth = dpkt.ethernet.Ethernet(buf)
    ip = eth.data
    tcp = ip.data
    try:
        if tcp.dport == 80 and len(tcp.data) > 0:
            http = dpkt.http.Request(tcp.data)
            if http.method == 'POST':
                print (http.headers['host'] + http.uri), http.body, http.method,
    except:
        pass

f.close()