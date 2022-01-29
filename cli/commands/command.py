from configparser import ConfigParser
from distutils.command.config import config
import logging
from attrs import define
from cli.datamodel.session import Session
from cli.network.networkmanager import NetworkManager

@define
class Command:
    cmd_name: str
    config: ConfigParser
    session: Session
    network_mgr: NetworkManager

    # base class init
    def __init__(self, commands_list, config, session, wsclient):
            self.config = config
            self.session = session
            self.network_mgr = wsclient
            commands_list[self.cmd_name] = self
            logging.debug("Command available " + self.__class__.__name__)

    async def do_command(self, *args):
        print('noop command')

    def show_help(self):
        help_text = getattr(self, "help_text", None)
        if help_text:
            print(help_text)
        else:
            print("Sorry, I can't help you with that")
