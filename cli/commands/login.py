import logging
from .command import Command

class Login(Command):
    cmd_name = 'login'
    help_text = """
Summary: Login to a server with our address book. This lets us find other users.
Usage: login [options]
Options:
    --user <name>,   your username
    --server <url>,  address of the signaling server (should be ws:// or wss://)
Examples:
    login
    login --user jason --server wss://clivrt-signaling-service-clivrt.apps.cluster-pt8dg.pt8dg.sandbox106.opentlc.com
"""

    def do_command(self, *args):
        # TODO arg handling to get user and uri

        try:
            self.session.ws_client.connect_to_signaling_server(self.session.singaling_host_path, self.session.my_name)
        except Exception as e:
            logging.error('login failed')
            logging.error(e)
            return
