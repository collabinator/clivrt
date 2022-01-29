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

    async def do_command(self, *args):
        try:
            if not self.network_mgr.is_connected():
                print('call requires an active connection to a signaling server - please login first.')
                return
        except Exception as e:
            logging.error('call failed')
            logging.error(e)
            return
        if not args:
            print('call requires a name for someone to call')
            return
        if self.session.connection_status.status == ConnectionStatusEnum.INCALL or self.session.connection_status.status == ConnectionStatusEnum.INGROUPCALL:
            print("hangup before calling someone else")
            return

        try:
            await self.network_mgr.invite_user_to_rtc(args[0])
            self.session.connection_status.status = ConnectionStatusEnum.INCALL
            self.session.connection_status.talking_to = args[0]
            # TODO connect WebRTC connection
        except Exception as e:
            logging.error('call failed')
            logging.error(e)
            return
