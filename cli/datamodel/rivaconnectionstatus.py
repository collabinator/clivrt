from attrs import define, asdict, frozen
from enum import Enum

class RivaConnectionStatusEnum(Enum):
    CONNECTED = 0
    NOTCONNECTED = 1

@define
class RivaConnectionStatus:
    status: RivaConnectionStatusEnum.NOTCONNECTED

    def getDescription(self):
        if self.status == RivaConnectionStatusEnum.CONNECTED:
            return 'tts-on'
        elif self.status == RivaConnectionStatusEnum.NOTCONNECTED:
            return 'tts-off'