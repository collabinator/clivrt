from configparser import ConfigParser
from dataclasses import Field
from typing import Optional
from attr import field
from attrs import define
from .connectionstatus import ConnectionStatus
from .connectionstatus import ConnectionStatusEnum
from .userslist import UsersList
import uuid
import platform

@define
class Session:
    config: ConfigParser
    users_list: UsersList = UsersList()
    connection_status = ConnectionStatus(ConnectionStatusEnum.NOTINCALL)
    my_signaling_id = str(uuid.uuid1())

    singaling_host_path: str = field(init=False)
    my_name: str = field(init=False)
    os_type: str = field(init=False)

    def __attrs_post_init__(self):
        self.users_list.update_available('[]')
        self.os_type = platform.system()
        self.my_name = ''
        self.singaling_host_path = ''

    def clear_session(self):
        # TODO getting error here --- 'Session' object attribute 'my_signaling_id' is read-only
        self.users_list.update_available('[]')
        self.singaling_host_path = ''
        self.my_name = ''
        self.my_signaling_id = str(uuid.uuid1())