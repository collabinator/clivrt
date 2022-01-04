import traceback
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.formatted_text import HTML
from commands import command 

better_completer = NestedCompleter.from_nested_dict({
    'call': None, 'hangup': None,                                   # 1-1 call
    'join': {}, 'leave': {},                                        # join leave rooms
    'login': None, 'logout': None, 'lookup': None, 'whoami': None,  # directory and addressbook
    'set': {                                                        # set various states (like availability)
        'donotdisturb': None,
        'away': None,
        'available': None
    },
    # 'debug': {                                                      # if the signaling server is offline we can manually connect peers
    #     'gen-video-offer': None,
    #     'gen-video-answer': {'from-video-offer': None},
    #     'use-video-answer': None
    # },
    'exit': None, 'quit': None                                      # exit
})

connection_status = 'Not in call'
availability_status = 'available'
def bottom_toolbar():
    # TODO future file data transfer progress
    # TODO video sent/received packets + bytes + frames + bitrate + etc...
    return HTML(connection_status + '/ <b>' + availability_status + '</b> / (Press ctrl+d to exit)')

def main():
    global connection_status
    global availability_status
    session = PromptSession(
        completer=better_completer, bottom_toolbar=bottom_toolbar)

    while True:
        try:
            text = session.prompt('> ')
            if not text:
                continue
            else:
                cmd_split = text.split()
            command, args = cmd_split[0], cmd_split[1:] or None

            if command == 'call':
                if not args:
                    print ("call requires a name of someone to call")
                    continue
                print("calling " + args[0])
                connection_status = 'In 1-1 call'                
                print("TODO")
            elif command == "hangup":
                print("hanging up")
                print("TODO")
                connection_status = 'Not in call'
            elif command == 'set':
                if not args:
                    print ("set requires additional arguments")
                    continue
                availability_status =  args[0]
                print("You are now " + args[0])
            elif command == 'exit' or command == 'quit':
                break
            else:
                print("Unsupported command: " + command)

        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        except Exception as e:
            traceback.print_exc()
    print('GoodBye!')

if __name__ == '__main__':
    main()