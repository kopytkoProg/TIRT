__author__ = 'michal'

from ComssServiceDevelopment.service import Service, ServiceController
from myObjectConnector.MyObjectConnector import MyInputObjectConnector


class MyPrinter(Service):
    def declare_outputs(self):
        pass

    def run(self):
        print('run')
        input_msg = self.get_input('In')
        """ :type: MyInputObjectConnector """

        while self.running():
            print('running')
            try:

                msg = input_msg.read()
                # print(input_msg.socket_connection.gethostname())
                print(msg)

            except Exception as e:
                print(e)
                input_msg.reopen_input()

    def declare_inputs(self):
        self.declare_input('In', MyInputObjectConnector(self))


if __name__ == "__main__":
    sc = ServiceController(MyPrinter, "service.json")
    sc.start()
