import logging
import websocket
from .command import Command
from cli.datamodel.connectionstatus import ConnectionStatusEnum
from cli import printf

class Hangup(Command):
    cmd_name = 'hangup'
    help_text = """
Summary: End the current call.
Usage: hangup
Examples:
    hangup
"""

    async def do_command(self, *args):
        logging.debug('hangup requested, connection status=' + self.session.connection_status.getDescription())
        if self.session.connection_status.status != ConnectionStatusEnum.INCALL and self.session.connection_status.status != ConnectionStatusEnum.INGROUPCALL:
            printf("<info>no call to hangup</info>")
            return

        try:
            # TODO disconnect WebRTC session
            await self.network_mgr.end_rtc()
            self.session.connection_status.status = ConnectionStatusEnum.NOTINCALL
            self.session.connection_status.group_name = ''
            self.session.connection_status.talking_to = ''
        except Exception as e:
            logging.error(e)
            printf(f'<error>hangup failed</error>')
            return

