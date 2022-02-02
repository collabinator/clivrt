import logging
from .command import Command
from cli.datamodel.connectionstatus import ConnectionStatusEnum
from cli import printf

class Say(Command):
    cmd_name = 'say'
    help_text = """
Summary:Say something to someone or to a channel of someones.
Usage: say <message>
Examples:
    say Don't raise your voice, improve your argument
    say A learning experience is one of those things that says, 'You know that thing you just did? Don't do that.
"""

    async def do_command(self, *args):
        try:
            if not self.network_mgr.is_connected():
                print("say requires an active connection - please login first")
                return
        except Exception as e:
            logging.error(e)
            printf('<error>say failed</error>')
            return

        if not args:
            printf('<info>say requires a message</info>')
            return
        message = ' '.join(args)
        logging.debug('saying ' + message)
        try:
            await self.network_mgr.broadcast_message(message)
        except Exception as e:
            logging.error(e)
            printf('<error>say failed</error>')
            return
