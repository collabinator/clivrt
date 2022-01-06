import logging
from .command import Command
from cli.datamodel.connectionstatus import ConnectionStatusEnum

class Say(Command):
    cmd_name = 'say'
    help_text = """
Summary:Say something to someone or to a channel of someones.
Usage: say <message>
Examples:
    say Don't raise your voice, improve your argument
    say A learning experience is one of those things that says, 'You know that thing you just did? Don't do that.
"""

    def do_command(self, *args):
        try:
            if not self.ws_client.is_connected():
                print("say requires an active connection - please login first")
                return
        except Exception as e:
            logging.error('say failed')
            logging.error(e)
            return

        if not args:
            print('say requires a message')
            return
        message = ' '.join(args)
        logging.debug('saying ' + message)
        try:
            self.ws_client.broadcast_message(message, self.session)
        except Exception as e:
            logging.error('say failed')
            logging.error(e)
            return
