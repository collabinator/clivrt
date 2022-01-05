import logging
from attrs import define
from cli.datamodel.session import Session

@define
class Command:
    cmd_name: str
    session: Session

    # base class init
    def __init__(self, commands_list, session):
            self.session = session
            commands_list[self.cmd_name] = self
            logging.debug("Command available " + self.__class__.__name__)

    def do_command(self, *args):
        print('noop command')

    def show_help(self):
        help_text = getattr(self, "help_text", None)
        if help_text:
            print(help_text)
        else:
            print("Sorry, I can't help you with that")
