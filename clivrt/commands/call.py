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
        status = self.connection_status;
        if not args:
            print('call requires a name for someone to call')
            return
        if status.status == ConnectionStatusEnum.INCALL or status.status == ConnectionStatusEnum.INGROUPCALL:
            print("hangup before calling someone else")
            return
        self.connection_status.status = ConnectionStatusEnum.NOTINCALL
        self.connection_status.talking_to = args[0]
        print('TODO actually do something to call ' + args[0])
