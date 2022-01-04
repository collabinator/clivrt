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
        print('hangup requested, connection status=' + self.connection_status.getDescription())
        if self.connection_status.status != ConnectionStatusEnum.INCALL and self.connection_status.status != ConnectionStatusEnum.INGROUPCALL:
            print("no call to hangup")
            return

        print('TODO actually hangup')
        self.connection_status.status = ConnectionStatusEnum.NOTINCALL
        self.connection_status.group_name = ''
        self.connection_status.talking_to = ''
