__author__ = 'michal'
import dpkt, pcap
pc = pcap.pcap()
pc.setfilter('icmp')
for ts, pkt in pc:
    print `dpkt.ethernet.Ethernet(pkt)`