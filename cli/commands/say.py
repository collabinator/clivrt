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
        if self.session.connection_status.status != ConnectionStatusEnum.INCALL and self.session.connection_status.status != ConnectionStatusEnum.INGROUPCALL:
            print("say requires an active connection")
            return
        if not args:
            print('say requires a message')
            return
        message = ' '.join(args)
        logging.debug('saying ' + message)
        try:
            self.session.ws_client.send_message(message)
        except Exception as e:
            logging.error('say failed')
            logging.error(e)
            return