from attrs import asdict, define, make_class, Factory

@define
class Command:
    def doit(self, *args):
        print('noop command')

    def show_help(self, cmd):
        help_text = getattr(self, "help_text", None)
        if help_text:
            print(help_text)
        else:
            print("Sorry, I can't help you with that")
