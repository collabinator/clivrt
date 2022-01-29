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

    async def do_command(self, *args):
        forced = False
        if args:
            for arg in args:
                if arg == '-f':
                    forced = True
                    break
        try:
            if not self.network_mgr.is_connected() and not forced:
                print('not logged in, use -f to attempt forcing a disconnect.')
                return
            await self.network_mgr.disconnect_from_signaling_server()
            self.session.clear_session()
        except Exception as e:
            logging.error('logout failed')
            logging.error(e)
            return
