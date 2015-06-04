__author__ = 'michal'

from ComssServiceDevelopment.service import Service, ServiceController
from myObjectConnector.MyObjectConnector import MyOutputObjectConnector
from MySniffer import start_sniffing




class MySnifferService(Service):
    def one_each_tcp_packet(self, data):

        self.stat['Sniffed tcp packets'] += 1

        output_msg = self.get_output('SniffService')
        output_stat_msg = self.get_output('MyPrinter')

        output_msg.my_send(data)
        output_stat_msg.my_send(self.stat)

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
        self.declare_output('MyPrinter', MyOutputObjectConnector(self))

    def __init__(self):
        print('=============== Start sniff service ===============')
        Service.__init__(self)
        self.stat = {'Sniffed tcp packets': 0}


if __name__ == "__main__":
    sc = ServiceController(MySnifferService, "service.json")
    sc.start()
