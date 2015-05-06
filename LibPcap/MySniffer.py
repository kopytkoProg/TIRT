from winpcapy import *
import time
import sys
import string
import platform
import socket
import dpkt
import netifaces
from struct import *
from LibPcap.TcpReassembler import TcpReassembler
from HttpReassembler import HttpReassembler


class IpAddress(Structure):
    _fields_ = [('byte1', c_ubyte),
                ('byte2', c_ubyte),
                ('byte3', c_ubyte),
                ('byte4', c_ubyte)]


class IpHeader(Structure):
    _fields_ = [('ver_ihl', c_ubyte),
                ('tos', c_ubyte),
                ('tlen', c_ushort),
                ('identification', c_ushort),
                ('flags_fo', c_ushort),
                ('ttl', c_ubyte),
                ('proto', c_ubyte),
                ('crc', c_ushort),
                ('saddr', IpAddress),
                ('daddr', IpAddress),
                ('op_pad', c_uint)]


class UdpHeader(Structure):
    _fields_ = [('sport', c_ushort),
                ('dport', c_ushort),
                ('len', c_ushort),
                ('crc', c_ushort)]


class TcpHeader(Structure):
    _fields_ = [('sport', c_ushort),
                ('dport', c_ushort),
                ('seqn', c_uint32),
                ('ackn', c_uint32),
                ('drf', c_ushort),
                ('window', c_ushort),
                ('checksum', c_ushort),
                ('urgentpointer', c_ushort),
                ('options', c_uint32)]


class Tcp:
    def __init__(self, th, data, sip, dip):
        self.SourceIp = sip
        self.DestinationIp = dip
        self.SourcePort = socket.ntohs(th.sport.real)
        self.DestinationPort = socket.ntohs(th.dport.real)
        # self.SequenceNumber = socket.ntohs(th.seqn.real)
        # self.AcknowledgmentNumber = socket.ntohs(th.ackn.real)
        self.Flags = socket.ntohs(th.drf.real) & 0x1FF
        self.WindowSize = socket.ntohs(th.window.real)
        self.Checksum = socket.ntohs(th.checksum.real)
        self.UrgentPointer = socket.ntohs(th.urgentpointer.real)
        self.Data = data

    def __str__(self):
        return '{0}:{2} --> {1}:{3} \n{4}'.format(self.SourceIp, self.DestinationIp, self.SourcePort,
                                                  self.DestinationPort, self.Data)


if platform.python_version()[0] == "3":
    raw_input = input
# /* prototype of the packet handler */
# void packet_handler(u_char *param, const struct pcap_pkthdr *header, const u_char *pkt_data);
PHAND = CFUNCTYPE(None, POINTER(c_ubyte), POINTER(pcap_pkthdr), POINTER(c_ubyte))


def ip4_addresses():
    ip_list = []
    for interface in netifaces.interfaces():
        if netifaces.AF_INET in netifaces.ifaddresses(interface):
            for link in netifaces.ifaddresses(interface)[netifaces.AF_INET]:
                if 'addr' in link.keys():
                    ip_list.append(link['addr'])
    return ip_list


def start_sniffing(callback):
    """
    Start sniffing. When tcp packet with HTTP header received then call callback
    :param callback:
    :return:
    """



    # Callback function invoked by libpcap for every incoming packet
    reas = TcpReassembler()
    http_reas = HttpReassembler()

    def _packet_handler(param, header, pkt_data):
        """
        This function is called when ip packet have been received.
        :param param:
        :param header:
        :param pkt_data:
        Only packet that have HTTP header will be processed
        """

        # convert the timestamp to readable format
        local_tv_sec = header.contents.ts.tv_sec
        ltime = time.localtime(local_tv_sec)
        timestr = time.strftime("%H:%M:%S", ltime)

        ih_address = addressof(pkt_data.contents) + 14
        ih = cast(ih_address, POINTER(IpHeader)).contents

        ip_len = (ih.ver_ihl.real & 0xf) * 4
        uh_address = ih_address + ip_len

        # Checksum count
        ih_bytes = cast(ih_address, POINTER(c_ushort * ((ih.ver_ihl.real & 0xf) * 2))).contents

        check_sum = 2
        ntochsum = []

        for b in ih_bytes:
            check_sum += socket.ntohs(b)
            ntochsum.append(socket.ntohs(b))

        check_sum &= 0xffff

        ip_data = cast(addressof(pkt_data.contents), POINTER(c_ubyte * (socket.ntohs(ih.tlen.real) + 14))).contents

        # -------------------------------------------------------

        a = []
        for b in ip_data:
            a.append(chr(b))

        buf = pack('c' * (socket.ntohs(ih.tlen.real) + 14), *a)

        eth = dpkt.ethernet.Ethernet(buf)
        ip = eth.data

        # print [link['addr'] for interface in netifaces.interfaces() if netifaces.AF_INET in netifaces.ifaddresses(interface) for link in netifaces.ifaddresses(interface)[netifaces.AF_INET] if 'addr' in link.keys()]

        #
        # for interface in netifaces.interfaces():
        # if netifaces.AF_INET in netifaces.ifaddresses(interface):
        # for link in netifaces.ifaddresses(interface)[netifaces.AF_INET]:
        #             if 'addr' in link.keys():
        #                 print link['addr']

        if isinstance(ip, dpkt.ip.IP) and (check_sum == 0xffff or check_sum == 0x00 or socket.inet_ntoa(ip.src) in ip4_addresses()):

            tcp = ip.data

            if isinstance(tcp, dpkt.tcp.TCP) and (tcp.sport == 80 or tcp.dport == 80):

                rp = reas.add_packet(tcp)
                # print rp
                for p in rp['data']:
                    r = http_reas.add_packet(p, rp['data'][p])

                    for http_datagram in r:
                        print r
                        eohh = '\r\n\r\n'

                        http_header = http_datagram[:http_datagram.find(eohh)]

                        http_data = []
                        for b in http_datagram[http_datagram.find(eohh) + len(eohh):]:
                            http_data.append(ord(b))

                        callback({'data': http_data, 'header': http_header})


                        # if len(tcp.data) > 0 and tcp.data.startswith('HTTP') or tcp.data.startswith(
                        # 'GET') or tcp.data.startswith('POST'):
                        #
                        # eohh = '\r\n\r\n'
                        #
                        #     http_header = tcp.data[:tcp.data.find(eohh)]
                        #
                        #     http_data = []
                        #     for b in tcp.data[tcp.data.find(eohh) + len(eohh):]:
                        #         http_data.append(ord(b))
                        #
                        #     callback({'data': http_data, 'header': http_header})

    packet_handler = PHAND(_packet_handler)
    alldevs = POINTER(pcap_if_t)()
    errbuf = create_string_buffer(PCAP_ERRBUF_SIZE)

    # Retrieve the device list
    if pcap_findalldevs(byref(alldevs), errbuf) == -1:
        print ("Error in pcap_findalldevs: %s\n" % errbuf.value)
        sys.exit(1)

    # Print the list
    i = 0
    try:
        d = alldevs.contents
    except:
        print ("Error in pcap_findalldevs: %s" % errbuf.value)
        print ("Maybe you need admin privilege?\n")
        sys.exit(1)
    while d:
        i = i + 1

        # addr = cast(addressof(d.addresses.contents.addr.contents)+4, POINTER(IpAddress)).contents
        # print d.addresses.contents.addr.contents
        # print dir(d.addresses.contents.addr.contents)
        # print addr.byte1, addr.byte2, addr.byte3, addr.byte4
        # print d.addresses.contents

        print("%d. %s" % (i, d.name))
        if d.description:
            print (" (%s)\n" % (d.description))
        else:
            print (" (No description available)\n")
        if d.next:
            d = d.next.contents
        else:
            d = False

    if i == 0:
        print ("\nNo interfaces found! Make sure WinPcap is installed.\n")
        sys.exit(-1)
    print ("Enter the interface number (1-%d):" % (i))

    inum = raw_input('--> ')
    if inum in string.digits:
        inum = int(inum)
    else:
        inum = 0

    if (inum < 1) | (inum > i):
        print ("\nInterface number out of range.\n")
        ## Free the device list
        pcap_freealldevs(alldevs)
        sys.exit(-1)
    # Jump to the selected adapter
    d = alldevs
    for i in range(0, inum - 1):
        d = d.contents.next
    # Open the device
    # Open the adapter
    d = d.contents
    adhandle = pcap_open_live(d.name, 65536, PCAP_OPENFLAG_PROMISCUOUS, 1000, errbuf)

    if adhandle == None:
        print("\nUnable to open the adapter. %s is not supported by Pcap-WinPcap\n" % d.contents.name)
        ## Free the device list
        pcap_freealldevs(alldevs)
        sys.exit(-1)
    print("\nlistening on %s...\n" % d.description)
    # At this point, we don't need any more the device list. Free it
    pcap_freealldevs(alldevs)
    # start the capture (we take only 15 packets)
    pcap_loop(adhandle, 0, packet_handler, None)
    pcap_close(adhandle)


if __name__ == "__main__":
    pass  # start_sniffing()

