import logging
from .command import Command

class Logout(Command):
    cmd_name = 'logout'
    help_text = """
Summary: Logout from a server with our address book. Usually, you'll want to login again immediately.
Usage: logout
Examples:
    logout
"""

    def do_command(self, *args):
        try:
            self.session.ws_client.disconnect()
        except Exception as e:
            logging.error('logout failed')
            logging.error(e)
            return
