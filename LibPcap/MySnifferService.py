__author__ = 'michal'

from ComssServiceDevelopment.service import Service, ServiceController
from myObjectConnector.MyObjectConnector import MyOutputObjectConnector
from MySniffer import Tcp, start_sniffing


class MySnifferService(Service):
    def one_each_tcp_packet(self, data):
        output_msg = self.get_output('SniffService')
        # print tcp.__str__()
        output_msg.my_send(data)

    def run(self):
        print('run')

        """ :type: MyOutputObjectConnector """
        start_sniffing(self.one_each_tcp_packet)
        # output_msg.my_send(post_fields)

    def declare_inputs(self):
        pass

    def declare_outputs(self):
        print('declare_outputs')
        self.declare_output('SniffService', MyOutputObjectConnector(self))

    def __init__(self):
        print('=============== Start sniff service ===============')
        Service.__init__(self)


if __name__ == "__main__":
    sc = ServiceController(MySnifferService, "service.json")
    sc.start()
