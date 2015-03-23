__author__ = 'michal'

from ComssServiceDevelopment.service import Service, ServiceController
from ComssServiceDevelopment.connectors.tcp.object_connector import InputMessageConnector


class MyService(Service):
    __doc__ = 'First service'

    def declare_inputs(self):
        print('declare_inputs')
        self.declare_input('In', InputMessageConnector(self))

    def declare_outputs(self):
        print('declare_outputs')
        pass

    def run(self):
        while True:
            msg = self.get_input('In').read_message()
            if msg is not None:
                print(msg)


if __name__ == "__main__":
    sc = ServiceController(MyService, "service.json")
    sc.start()


