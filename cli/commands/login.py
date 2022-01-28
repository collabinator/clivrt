import argparse
import logging
from attr import define
from .command import Command
import names

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
        config_defaults = self.config.defaults()
        user = config_defaults.get('username', 'Anon'+names.get_first_name())
        server = config_defaults.get('signalinghosturl', 'dummy')
        if args:
            parser = argparse.ArgumentParser()
            parser.add_argument('--user')
            parser.add_argument('--server')
            argsdict, argsunknown = parser.parse_known_args(args)
            if (argsdict.user): user = argsdict.user
            if (argsdict.server): server = argsdict.server
            for unk in argsunknown: logging.warning("Login can't handle unknown option:" + unk)
        try:
            self.session.my_name = user
            self.session.singaling_host_path = server
            logging.debug('connecting to signaling server ' + server + ' as user ' + user)
            self.ws_client.connect_to_signaling_server(server, user)
        except Exception as e:
            logging.error('login failed')
            logging.error(e)
            return
