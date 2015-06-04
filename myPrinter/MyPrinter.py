__author__ = 'michal'
import threading, sys
from ComssServiceDevelopment.service import Service, ServiceController
from myObjectConnector.MyObjectConnector import MyInputObjectConnector
from threading import Thread


class MyPrinter(Service):
    def __init__(self):
        Service.__init__(self)
        self.stat = {}
        self.lock = threading.Lock()

    def declare_outputs(self):
        pass

    def update_dict(self, d):

        self.lock.acquire(True)
        for k in d.keys():
            self.stat[k] = d[k]
        sys.stdout.write("\033[F")  # Cursor up one line
        print self.stat
        self.lock.release()

    def thread(self, i):

        input_msg = self.get_input(i)
        """ :type: MyInputObjectConnector """

        while self.running():

            try:

                msg = input_msg.read()
                # print(input_msg.socket_connection.gethostname())
                # print(msg)
                self.update_dict(msg)

            except Exception as e:
                print(e)
                input_msg.reopen_input()

    def run(self):
        print('run')

        inputs = [('In1', ), ('In2', ), ('In3', ), ('In4', ), ('In5', )]
        t = []

        for i in inputs:
            thread = Thread(target=self.thread, args=i)
            thread.start()
            t.append(thread)

        for i in t:
            i.join()

    def declare_inputs(self):
        self.declare_input('In1', MyInputObjectConnector(self))
        self.declare_input('In2', MyInputObjectConnector(self))
        self.declare_input('In3', MyInputObjectConnector(self))
        self.declare_input('In4', MyInputObjectConnector(self))
        self.declare_input('In5', MyInputObjectConnector(self))


if __name__ == "__main__":
    sc = ServiceController(MyPrinter, "service.json")
    sc.start()
