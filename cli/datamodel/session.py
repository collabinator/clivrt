from attrs import define
from .connectionstatus import ConnectionStatus
from .connectionstatus import ConnectionStatusEnum
from .userslist import UsersList
import names
import uuid

@define
class Session:
    users_list: UsersList = UsersList()
    connection_status = ConnectionStatus(ConnectionStatusEnum.NOTINCALL)
    my_name = names.get_first_name()
    my_signaling_id = str(uuid.uuid1())
    # TODO set this from env vars somewhere
    singaling_host_path = 'wss://clivrt-signaling-service-clivrt.apps.cluster-pt8dg.pt8dg.sandbox106.opentlc.com'

    def __attrs_post_init__(self):
        # self.ws_client.session = self
        self.users_list.update_available('[]')

    # def clear_session():
    #     self.users_list.updateAvailable('[]')
    #     return