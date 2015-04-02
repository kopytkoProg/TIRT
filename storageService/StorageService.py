__author__ = 'michal'

from ComssServiceDevelopment.service import Service, ServiceController
# from ComssServiceDevelopment.connectors.tcp.object_connector import InputObjectConnector
from myObjectConnector.MyObjectConnector import MyInputObjectConnector
from Storage import Storage


class StorageService(Service):
    storage = None

    def run(self):
        print('run')
        input_msg = self.get_input('In')
        """ :type: MyInputObjectConnector """
        exception = False
        while self.running() and not exception:
            msg = input_msg.my_read()
            print("StorageService:")
            print(msg)
            # print(msg)
            self.storage.append_to_file(msg)

    def declare_inputs(self):
        print('declare_inputs')
        self.declare_input('In', MyInputObjectConnector(self))

    def declare_outputs(self):
        print('declare_outputs')
        pass

    def __init__(self):
        print('=============== Start storage service ===============')
        Service.__init__(self)
        self.storage = Storage()


if __name__ == "__main__":
    sc = ServiceController(StorageService, "service.json")
    sc.start()

