__author__ = 'michal'


from ComssServiceDevelopment.development import DevServiceController
from myObjectConnector.MyObjectConnector import MyInputObjectConnector


service_controller = DevServiceController('service.json')
service_controller.declare_connection("SniffService", MyInputObjectConnector(service_controller))

if __name__ == "__main__":
    __doc__ = 'MySnifferService test'

    input_con = service_controller.get_connection("SniffService")
    while True:

            msg = input_con.my_read()
            print(msg)


