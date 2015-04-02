__author__ = 'michal'


from ComssServiceDevelopment.development import DevServiceController
from ComssServiceDevelopment.connectors.tcp.object_connector import OutputObjectConnector


service_controller = DevServiceController('service.json')
service_controller.declare_connection("In", OutputObjectConnector(service_controller))

if __name__ == "__main__":
    __doc__ = 'test of StorageService'

    input_con = service_controller.get_connection("In")
    input_con.send(['Som', 'String'])
    input_con.send(['Som', 'String'])
    raw_input("Press Enter to continue...")
    input_con.close()