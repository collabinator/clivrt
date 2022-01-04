from commands import command

class Call(Command):
    cmd = 'call'
    help_text = """
Summary: Place a call to someone else who is known in the global address book.
Usage: call <person>
Examples:
    call jason
    call andy
"""

    def do_command(self, *args):
        status = self.connection_status;

        if not args:
            print('call requires a name for someone to call')
            return
        if status == 'In 1-1 call':
            print("hangup before calling someone else")
            return
        print('TODO actually do something to call ' + args[0])

    def show_help(self, cmd):
        print('TODO help for call')