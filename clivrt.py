import traceback
from attr import field
from attrs import asdict, define, make_class, Factory
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.formatted_text import HTML
from cli.commands.call import Call
from cli.commands.hangup import Hangup
from cli.datamodel.connectionstatus import ConnectionStatus
from cli.datamodel.connectionstatus import ConnectionStatusEnum

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

connection_status = ConnectionStatus(ConnectionStatusEnum.NOTINCALL)
availability_status = 'available'
def bottom_toolbar():
    # TODO future file data transfer progress
    # TODO video sent/received packets + bytes + frames + bitrate + etc...
    return HTML(connection_status.getDescription() + '/ <b>' + availability_status + '</b> / (Press ctrl+d to exit)')

def main():
    global connection_status
    global availability_status
    
    commands = {}
    dummy = Call(commands, connection_status)
    dummy = Hangup(commands, connection_status)
    # load all the commands availble from the commands folder
    # TODO

    session = PromptSession(
        completer=better_completer, bottom_toolbar=bottom_toolbar)

    while True:
        try:
            text = session.prompt('> ')
            if not text:
                continue
            else:
                input_cmd_split = text.split()
            input_cmd_name, input_cmd_args = input_cmd_split[0], input_cmd_split[1:]

            command = commands.get(input_cmd_name) or None
            if not command:
                print("Unsupported command " + input_cmd_name)
                continue
            command.do_command(*input_cmd_args)

            # if input_cmd_name == 'call':
            #     if not input_cmd_args:
            #         print ("call requires a name of someone to call")
            #         continue
            #     print("calling " + input_cmd_args[0])
            #     connection_status = 'In 1-1 call'                
            #     print("TODO")
            # elif input_cmd_name == "hangup":
            #     print("hanging up")
            #     print("TODO")
            #     connection_status = 'Not in call'
            # elif input_cmd_name == 'set':
            #     if not input_cmd_args:
            #         print ("set requires additional arguments")
            #         continue
            #     availability_status =  input_cmd_args[0]
            #     print("You are now " + input_cmd_args[0])
            # elif input_cmd_name == 'exit' or input_cmd_name == 'quit':
            #     break
            # else:
            #     print("Unsupported command: " + input_cmd_name)

        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        except Exception as e:
            traceback.print_exc()
    print('GoodBye!')

if __name__ == '__main__':
    main()