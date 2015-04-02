__author__ = 'michal'

from ComssServiceDevelopment.connectors.tcp.object_connector import InputObjectConnector, OutputObjectConnector


class MyInputObjectConnector(InputObjectConnector):
    def reopen_input(self):
        """ Can be used to reinitialize socket (when connection was ended)"""
        self.clear_socket_connection()
        self.init()

    def my_read(self):

        try:
            msg = self.read()
        except:
            self.reopen_input()
            return self.read()
        else:
            return msg


class MyOutputObjectConnector(OutputObjectConnector):
    def reopen_output(self):
        """ Can be used to reinitialize socket (when connection was ended)"""
        self.close()
        self.init()

    def reopen_if_closed(self):
        if self.socket is None:
            self.reopen_output()

    def my_send(self, msg):
        try:
            self.send(msg)
        except:
            self.reopen_output()
            self.send(msg)