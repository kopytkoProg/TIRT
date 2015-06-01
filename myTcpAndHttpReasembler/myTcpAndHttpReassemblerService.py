__author__ = 'michal'

from ComssServiceDevelopment.service import Service, ServiceController
from myObjectConnector.MyObjectConnector import MyOutputObjectConnector, MyInputObjectConnector
import dpkt
from LibPcap.TcpReassembler import TcpReassembler
from LibPcap.HttpReassembler import HttpReassembler

reas = TcpReassembler()
http_reas = HttpReassembler()


class MyTcpAndHttpReassemblerService(Service):
    def one_each_tcp_packet(self, data):

        output_msg = self.get_output('SelectorService')
        output_msg.my_send(data)

    def run(self):
        print('run')

        input_msg = self.get_input('SniffService')
        """ :type: MyInputObjectConnector """

        exception = False
        while self.running() and not exception:

            msg = input_msg.my_read()
            str = ''.join([chr(c) for c in msg['tcp']])

            tcp = dpkt.tcp.TCP(str)

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

                    self.one_each_tcp_packet({'data': http_data, 'header': http_header})


    def declare_inputs(self):
        self.declare_input('SniffService', MyInputObjectConnector(self))

    def declare_outputs(self):
        print('declare_outputs')
        self.declare_output('SelectorService', MyOutputObjectConnector(self))

    def __init__(self):
        print('=============== Start sniff service ===============')
        Service.__init__(self)


if __name__ == "__main__":
    sc = ServiceController(MyTcpAndHttpReassemblerService, "service.json")
    sc.start()
