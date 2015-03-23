__author__ = 'michal'

from ComssServiceDevelopment.development import DevServiceController
from ComssServiceDevelopment.connectors.tcp.object_connector import OutputMessageConnector

service_controller = DevServiceController('service.json')
service_controller.declare_connection("In", OutputMessageConnector(service_controller))

if __name__ == "__main__":
    __doc__ = 'test of MyService'
    service_controller.get_connection("In").send('SomStringToService')
    service_controller.get_connection("In").close()