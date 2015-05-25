__author__ = 'michal'

from ComssServiceDevelopment.service import Service, ServiceController
from myObjectConnector.MyObjectConnector import MyInputObjectConnector, MyOutputObjectConnector
from selector.HeaderParser import HeaderParser, HttpRequest, HttpResponse


class SelectorService(Service):
    def run(self):
        print('run')
        input_msg = self.get_input('In')
        """ :type: MyInputObjectConnector """
        output_msg = self.get_output('Out')
        """ :type: MyOutputObjectConnector """

        exception = False
        while self.running() and not exception:

            msg = input_msg.my_read()

            h = HeaderParser(msg['header']).parse()
            # print msg
            if isinstance(h, HttpRequest) and h.method == 'POST':
                if 'Content-Encoding' not in h.fields \
                        and 'Content-Type' in h.fields \
                        and h.fields['Content-Type'].startswith("application/x-www-form-urlencoded"):
                    print HeaderParser.data_to_string(msg['data'])
                    output_msg.my_send(
                        {
                            'header': msg['header'],  # raw header
                            'fields': h.fields,  # header fields
                            'request_line': h.request_line,   # request line
                            'data': HeaderParser.data_to_string(msg['data'])  # data
                        })

    def declare_inputs(self):
        print('declare_inputs')
        self.declare_input('In', MyInputObjectConnector(self))

    def declare_outputs(self):
        print('declare_outputs')
        self.declare_output('Out', MyOutputObjectConnector(self))

    def __init__(self):
        print('=============== Start SelectorService ===============')
        Service.__init__(self)


if __name__ == "__main__":
    sc = ServiceController(SelectorService, "service.json")
    sc.start()
