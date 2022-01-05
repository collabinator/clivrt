import logging

import websocket
from .command import Command
from cli.datamodel.connectionstatus import ConnectionStatusEnum

class Hangup(Command):
    cmd_name = 'hangup'
    help_text = """
Summary: End the current call.
Usage: hangup
Examples:
    hangup
"""

    def do_command(self, *args):
        logging.debug('hangup requested, connection status=' + self.session.connection_status.getDescription())
        if self.session.connection_status.status != ConnectionStatusEnum.INCALL and self.session.connection_status.status != ConnectionStatusEnum.INGROUPCALL:
            print("no call to hangup")
            return

        try:
            # TODO disconnect WebRTC session
            self.session.ws_client.endRTC()
            self.session.connection_status.status = ConnectionStatusEnum.NOTINCALL
            self.session.connection_status.group_name = ''
            self.session.connection_status.talking_to = ''
        except Exception as e:
            logging.error('hangup failed')
            logging.error(e)
            return

