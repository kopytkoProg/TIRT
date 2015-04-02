__author__ = 'michal'


from ComssServiceDevelopment.development import DevServiceController
from ComssServiceDevelopment.connectors.tcp.object_connector import OutputObjectConnector


service_controller = DevServiceController('service.json')
service_controller.declare_connection("In", OutputObjectConnector(service_controller))

if __name__ == "__main__":
    __doc__ = 'test of StorageService'

    with open('Post.txt', 'rU') as f:

        read_data = f.read()
        input_con = service_controller.get_connection("In")
        input_con.send(read_data)
        raw_input("Press Enter to continue...")
        input_con.close()