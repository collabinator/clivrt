import logging
from .command import Command
from cli.datamodel.connectionstatus import ConnectionStatusEnum
from cli import printf

class Local(Command):
    cmd_name = 'local'
    help_text = """
Summary:Test encoding of your local webcam.
Usage: local
"""

    async def do_command(self, *args):
        message = ' '.join(args)

        try:
            await self.network_mgr.add_media_tracks()
            
        except Exception as e:
            logging.error(e)
            printf(f'<error>local failed</error>')
            return