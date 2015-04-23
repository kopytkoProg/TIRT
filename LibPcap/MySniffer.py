from winpcapy import *
import time
import sys
import string
import platform
import socket
import dpkt
from struct import *


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


def start_sniffing(callback):
    """
    Start sniffing. When tcp packet with HTTP header received then call callback
    :param callback:
    :return:
    """
    # Callback function invoked by libpcap for every incoming packet
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
        for b in ih_bytes:
            check_sum += b

        check_sum &= 0xffff

        ip_data = cast(addressof(pkt_data.contents), POINTER(c_ubyte * (socket.ntohs(ih.tlen.real) + 14))).contents

        # -------------------------------------------------------

        a = []
        for b in ip_data:
            a.append(chr(b))

        buf = pack('c' * (socket.ntohs(ih.tlen.real) + 14), *a)

        if check_sum == 0xffff:
            try:
                eth = dpkt.ethernet.Ethernet(buf)
                ip = eth.data
                tcp = ip.data

                if (tcp.dport == 80 or tcp.sport == 80) and len(tcp.data) > 0:
                    callback(tcp.data)
                    # http = dpkt.http.Request(tcp.data)
            except:
                pass

        # -------------------------------------------------------



        #
        #
        #
        # if ih.proto.real == 0x06 and check_sum == 0xffff:
        #
        #     th_address = uh_address
        #     th = cast(th_address, POINTER(TcpHeader)).contents
        #
        #     # print str(ih.saddr.byte1.real) + "." + str(ih.saddr.byte2.real) + "." + str(ih.saddr.byte3.real) + "." + str(
        #     # ih.saddr.byte4.real) + ":" + str(socket.ntohs(uh.sport.real))
        #     #
        #     # print str(ih.daddr.byte1.real) + "." + str(ih.daddr.byte2.real) + "." + str(ih.daddr.byte3.real) + "." + str(
        #     # ih.daddr.byte4.real) + ":" + str(socket.ntohs(uh.dport.real))
        #
        #     tcp_data_offset = ((socket.ntohs(th.drf.real) & 0xf000) >> 12) * 4
        #     tcp_data_start = tcp_data_offset + th_address
        #     tcp_data_end = ih_address + socket.ntohs(ih.tlen.real)
        #
        #     tcp_data = cast(tcp_data_start, POINTER(c_ubyte * (tcp_data_end - tcp_data_start))).contents
        #
        #     # print 'th_address: ' + str(th_address)
        #     # print 'tcp_data_offset: ' + str(tcp_data_offset)
        #     # print 'tcp_data_start: ' + str(tcp_data_start)
        #     # print 'tcp_data_end: ' + str(tcp_data_end)
        #     # print 'tcp_data_end: ' + str(tcp_data_end)
        #     # print 'ih.tlen.real: ' + str(socket.ntohs(ih.tlen.real))
        #
        #     s = ''
        #     l = []
        #     for c in tcp_data:
        #         s += chr(c) if c < 128 else '[' + str(c) + ']'
        #         l.append(c)
        #
        #     # print bytearray(l).decode('utf-8')
        #     # print s
        #     if s.startswith('HTTP') or s.startswith('GET') or s.startswith('POST'):
        #         tcp = Tcp(th,
        #                   l,
        #                   str(ih.saddr.byte1.real) + "." + str(ih.saddr.byte2.real) + "." + str(
        #                       ih.saddr.byte3.real) + "." + str(
        #                       ih.saddr.byte4.real),
        #                   str(ih.daddr.byte1.real) + "." + str(ih.daddr.byte2.real) + "." + str(
        #                       ih.daddr.byte3.real) + "." + str(
        #                       ih.daddr.byte4.real)
        #                   )
        #
        #         callback(tcp)
        #
                # print("%s,%.6d len:%d" % (timestr, header.contents.ts.tv_usec, header.contents.len))


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
    start_sniffing()
