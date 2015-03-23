__author__ = 'michal'

from ComssServiceDevelopment.service import Service, ServiceController
from ComssServiceDevelopment.connectors.tcp.object_connector import InputObjectConnector
from Storage import Storage


class StorageService(Service):
    storage = None

    def run(self):
        print('run')
        input_msg = self.get_input('In')
        """ :type: InputObjectConnector """
        exception = False
        while self.running() and not exception:

            try:

                msg = input_msg.read()
                print(msg)
                self.storage.append_to_file(msg)

            except Exception:
                # print(a)
                self.reopen_input()

    def declare_inputs(self):
        print('declare_inputs')
        self.declare_input('In', InputObjectConnector(self))

    def declare_outputs(self):
        print('declare_outputs')
        pass

    def __init__(self):
        print('=============== Start storage service ===============')
        Service.__init__(self)
        self.storage = Storage()

    def reopen_input(self):
        input_msg = self.get_input('In')
        """ :type: InputObjectConnector """
        input_msg.clear_socket_connection()
        input_msg.init()


if __name__ == "__main__":
    sc = ServiceController(StorageService, "service.json")
    sc.start()

