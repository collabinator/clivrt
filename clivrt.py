import traceback
import logging
from attr import field
from attrs import asdict, define, make_class, Factory
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.formatted_text import HTML
from cli.commands.call import Call
from cli.commands.hangup import Hangup
from cli.commands.say import Say
from cli.datamodel.session import Session
from cli.commands.login import Login
from cli.commands.logout import Logout

logging.basicConfig(level=logging.DEBUG)

better_completer = NestedCompleter.from_nested_dict({
    'call': None, 'hangup': None,                                   # 1-1 call
    'join': {}, 'leave': {},                                        # join leave rooms
    'login': None, 'logout': None, 'lookup': None, 'whoami': None,  # directory and addressbook
    'set': {                                                        # set various states (like availability)
        'donotdisturb': None,
        'away': None,
        'available': None
    },
    'say': None,                                                      # text chat can be done via signaling server
    # 'carrierpigeon': {                                              # if the signaling server is offline we can manually connect peers
    #     'gen-video-offer': None,
    #     'gen-video-answer': {'from-video-offer': None},
    #     'use-video-answer': None
    # },
    'exit': None, 'quit': None                                      # exit
})

session = Session()
availability_status = 'available'
def bottom_toolbar():
    # TODO future file data transfer progress
    # TODO video sent/received packets + bytes + frames + bitrate + etc...
    return HTML(session.connection_status.getDescription() + '/ <b>' + availability_status + '</b> / (Press ctrl+d to exit)')

def main():
    commands = {}
    dummy = Call(commands, session)
    dummy = Hangup(commands, session)
    dummy = Say(commands, session)
    dummy = Login(commands, session)
    dummy = Logout(commands, session)
    # TODO load all the commands availble from the commands folder vs manually like above (also loop import classes)

    prompt_session = PromptSession(
        completer=better_completer, bottom_toolbar=bottom_toolbar)

    while True:
        try:
            text = prompt_session.prompt('> ')
            if not text:
                continue
            else:
                input_cmd_split = text.split()
            input_cmd_name, input_cmd_args = input_cmd_split[0], input_cmd_split[1:]

            command = commands.get(input_cmd_name) or None
            if not command:
                print("Unsupported command " + input_cmd_name)
                continue

            show_help = False
            for arg in input_cmd_args:  # common args processing done here (versus in every command)
                if arg == '-h':
                    show_help = True
                    break

            if show_help:
                command.show_help()
            else:
                command.do_command(*input_cmd_args)

        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        except Exception as e:
            traceback.print_exc()
    print('GoodBye!')

if __name__ == '__main__':
    main()