from modules.server import Server
from registry.ibm_cloud import IbmCloud
server = Server('YOUR_IP', 'YOUR_SSH_KEY', IbmCloud())
server.setup()