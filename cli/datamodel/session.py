from attrs import define
from cli.network.websockclient import WebSockClient
from .connectionstatus import ConnectionStatus
from .connectionstatus import ConnectionStatusEnum
import names

@define
class Session:
    ws_client: WebSockClient = WebSockClient()
    connection_status = ConnectionStatus(ConnectionStatusEnum.NOTINCALL)
    my_name = names.get_first_name()
    singaling_host_path = 'wss://clivrt-signaling-service-clivrt.apps.cluster-pt8dg.pt8dg.sandbox106.opentlc.com'