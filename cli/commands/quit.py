import sys
from .command import Command

class Quit(Command):
    cmd_name = 'quit'
    help_text = """
Summary: Quit the cli app.
Usage: quit
Examples:
    quit
"""

    def do_command(self, *args):
        print('GoodBye!')
        sys.exit(0)
