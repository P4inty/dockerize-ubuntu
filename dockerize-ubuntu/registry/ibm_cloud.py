from registry.registry import Registry

class IbmCloud(Registry):
    def setup(self, connection):
        connection.run('curl -fsSL https://clis.cloud.ibm.com/install/linux | sh')
        connection.run("ibmcloud plugin install container-registry -r 'IBM Cloud'")
        print('---ENTER YOUR IBM CREDENTIALS---')
        connection.run('ibmcloud login -a https://cloud.ibm.com')
        connection.run('ibmcloud cr login')