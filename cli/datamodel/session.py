from attrs import define
from cli.network.websockclient import WebSockClient
from .connectionstatus import ConnectionStatus
from .connectionstatus import ConnectionStatusEnum
import names
import uuid

@define
class Session:
    ws_client: WebSockClient = WebSockClient()
    connection_status = ConnectionStatus(ConnectionStatusEnum.NOTINCALL)
    my_name = names.get_first_name()
    my_signaling_id = str(uuid.uuid1())
    singaling_host_path = 'ws://localhost:8080'