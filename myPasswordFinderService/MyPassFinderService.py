__author__ = 'michal'

from ComssServiceDevelopment.service import Service, ServiceController
from myObjectConnector.MyObjectConnector import MyInputObjectConnector, MyOutputObjectConnector
from myPasswordFinderService.MyPasswordFinder import MyPasswordFinder


class MyPassFinderService(Service):
    def run(self):
        print('run')
        input_msg = self.get_input('In')
        """ :type: MyInputObjectConnector """

        output_msg_2_storage = self.get_output('StorageService')
        """ :type: MyOutputObjectConnector """

        output_msg_2_printer = self.get_output('MyPrinter')
        """ :type: MyOutputObjectConnector """

        output_stat_msg = self.get_output('MyPrinterStat')
        """ :type: MyOutputObjectConnector """

        exception = False
        while self.running() and not exception:

            msg = input_msg.my_read()

            post_fields = None

            if type(msg) is str:
                post_fields = self.my_password_finder.find_pass_in_http_message(msg)
            elif type(msg) is dict:
                # print msg
                post_fields = self.my_password_finder.find_pass(msg)

            if post_fields is not None:
                print ('MyPassFinderService:')
                print (post_fields)

                output_msg_2_printer.my_send(post_fields)
                output_msg_2_storage.my_send(post_fields)
                self.stat['Selected passwords'] += 1
                output_stat_msg.my_send(self.stat)

    def declare_inputs(self):
        print('declare_inputs')
        self.declare_input('In', MyInputObjectConnector(self))

    def declare_outputs(self):
        print('declare_outputs')
        self.declare_output('StorageService', MyOutputObjectConnector(self))
        self.declare_output('MyPrinter', MyOutputObjectConnector(self))
        self.declare_output('MyPrinterStat', MyOutputObjectConnector(self))

    def __init__(self):
        print('=============== Start storage service ===============')
        Service.__init__(self)
        self.stat = {'Selected passwords': 0}
        self.my_password_finder = MyPasswordFinder()


if __name__ == "__main__":
    sc = ServiceController(MyPassFinderService, "service.json")
    sc.start()
