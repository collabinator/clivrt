import logging
from .command import Command
from cli.datamodel.connectionstatus import ConnectionStatusEnum

class Call(Command):
    cmd_name = 'call'
    help_text = """
Summary: Place a call to someone else who is known in the global address book.
Usage: call <person>
Examples:
    call jason
    call andy
"""

    def do_command(self, *args):
        logging.debug('call requested, connection status=' + self.session.connection_status.getDescription())
        if not args:
            print('call requires a name for someone to call')
            return
        if self.session.connection_status.status == ConnectionStatusEnum.INCALL or self.session.connection_status.status == ConnectionStatusEnum.INGROUPCALL:
            print("hangup before calling someone else")
            return

        try:
            self.session.ws_client.inviteUserToRTC(args[0])
            self.session.connection_status.status = ConnectionStatusEnum.INCALL
            self.session.connection_status.talking_to = args[0]
            # TODO connect WebRTC connection
        except Exception as e:
            logging.error('call failed')
            logging.error(e)
            return
