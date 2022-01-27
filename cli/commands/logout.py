import logging
from .command import Command

class Logout(Command):
    cmd_name = 'logout'
    help_text = """
Summary: Logout from a server with our address book. Usually, you'll want to login again immediately.
Usage: logout
Options:
    -f, attempt to force logout
Examples:
    logout
"""

    def do_command(self, *args):
        forced = False
        if args:
            for arg in args:
                if arg == '-f':
                    forced = True
                    break
        try:
            if not self.ws_client.is_connected() and not forced:
                print('not logged in, use -f to attempt forcing a disconnect.')
                return
            self.ws_client.disconnect()
        except Exception as e:
            logging.error('logout failed')
            logging.error(e)
            return
