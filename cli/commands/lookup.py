import logging
from .command import Command

class Lookup(Command):
    cmd_name = 'lookup'
    help_text = """
Summary: Lists all the available users found in the server's address book.
Usage: lookup
Examples:
    lookup
"""

    def do_command(self, *args):
        try:
            if not self.ws_client.is_connected():
                print('lookup requires an active connection to a signaling server - please login first.')
                return
        except Exception as e:
            logging.error('lookup failed')
            logging.error(e)
            return

        if self.session.users_list is None or len(self.session.users_list.available_users) < 1:
            print('no users found')
            return

        print('The following users are available:')
        for user in self.session.users_list.available_users:
            print(user)
 
