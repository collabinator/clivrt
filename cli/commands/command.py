from attrs import define
from cli.datamodel.connectionstatus import ConnectionStatus

@define
class Command:
    cmd_name: str
    connection_status: ConnectionStatus

    # base class init
    def __init__(self, commands_list, connection_status):
            self.connection_status = connection_status
            commands_list[self.cmd_name] = self
            print("Command available " + self.__class__.__name__)

    def do_command(self, *args):
        print('noop command')

    def show_help(self, cmd_name):
        help_text = getattr(self, "help_text", None)
        if help_text:
            print(help_text)
        else:
            print("Sorry, I can't help you with that")
