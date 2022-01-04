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
        print('call requested, connection status=' + self.connection_status.getDescription())
        if not args:
            print('call requires a name for someone to call')
            return
        if self.connection_status.status == ConnectionStatusEnum.INCALL or self.connection_status.status == ConnectionStatusEnum.INGROUPCALL:
            print("hangup before calling someone else")
            return

        print('TODO actually do something to call ' + args[0])
        self.connection_status.status = ConnectionStatusEnum.INCALL
        self.connection_status.talking_to = args[0]

