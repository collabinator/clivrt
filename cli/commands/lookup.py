import logging
from cli import printf
from .command import Command

class Lookup(Command):
    cmd_name = 'lookup'
    help_text = """
Summary: Lists all the available users found in the server's address book.
Usage: lookup
Examples:
    lookup
"""

    async def do_command(self, *args):
        try:
            if not self.network_mgr.is_connected():
                printf(f'<info>lookup requires an active connection to a signaling server - please login first.</info>')
                return
        except Exception as e:
            logging.error(e)
            printf(f'<error>users lookup failed</error>')
            return

        if self.session.users_list is None or len(self.session.users_list.available_users) < 1:
            printf(f'<info>no users found</info>')
            return

        printf(f'<info>The following users are available:</info>')
        printf(self.session.users_list.available_users)

