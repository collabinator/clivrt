from attrs import define, asdict, frozen
from enum import Enum

class ConnectionStatusEnum(Enum):
    INCALL = 0
    NOTINCALL = 1
    INGROUPCALL = 2

@define
class ConnectionStatus:
    status: ConnectionStatusEnum.NOTINCALL
    group_name: str = None
    talking_to: str = None

    def getDescription(self):
        if self.status == ConnectionStatusEnum.INCALL:
            return '1-1 call (' + self.talking_to + ')'
        elif self.status == ConnectionStatusEnum.NOTINCALL:
            return 'No connection'
        elif self.status == ConnectionStatusEnum.INGROUPCALL:
            return 'room: ' + self.group_name
