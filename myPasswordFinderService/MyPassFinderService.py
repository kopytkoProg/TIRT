__author__ = 'michal'

from ComssServiceDevelopment.service import Service, ServiceController
from myObjectConnector.MyObjectConnector import MyInputObjectConnector, MyOutputObjectConnector
from myPasswordFinderService.MyPasswordFinder import MyPasswordFinder


class MyPassFinderService(Service):
    def run(self):
        print('run')
        input_msg = self.get_input('In')
        """ :type: MyInputObjectConnector """
        output_msg = self.get_output('StorageService')
        """ :type: MyOutputObjectConnector """

        exception = False
        while self.running() and not exception:

            msg = input_msg.my_read()
            post_fields = self.my_password_finder.find_pass(msg)
            if post_fields is not None:
                print ('MyPassFinderService:')
                print (post_fields)

                output_msg.my_send(post_fields)

    def declare_inputs(self):
        print('declare_inputs')
        self.declare_input('In', MyInputObjectConnector(self))

    def declare_outputs(self):
        print('declare_outputs')
        self.declare_output('StorageService', MyOutputObjectConnector(self))

    def __init__(self):
        print('=============== Start storage service ===============')
        Service.__init__(self)
        self.my_password_finder = MyPasswordFinder()


if __name__ == "__main__":
    sc = ServiceController(MyPassFinderService, "service.json")
    sc.start()
