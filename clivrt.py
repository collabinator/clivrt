import configparser
from pickletools import TAKEN_FROM_ARGUMENT1
import traceback
import logging
import prompt_toolkit
import asyncio
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter, NestedCompleter
from prompt_toolkit.shortcuts.prompt import prompt
from cli.commands.call import Call
from cli.commands.hangup import Hangup
from cli.commands.say import Say
from cli.commands.login import Login
from cli.commands.logout import Logout
from cli.commands.quit import Quit
from cli.commands.lookup import Lookup
from cli.datamodel.session import Session
from cli.network.networkmanager import NetworkManager
from cli import printf
from cli.media import videotransformtrack

config = configparser.ConfigParser()
config.read('.clivrt')
logging.basicConfig(level=logging.WARNING)
loglevel_str = config.defaults().get('loglevel', 'WARNING')
if 'DEBUG' in loglevel_str.upper(): logging.getLogger().setLevel(logging.DEBUG)
if 'INFO' in loglevel_str.upper(): logging.getLogger().setLevel(logging.INFO)
if 'WARN' in loglevel_str.upper(): logging.getLogger().setLevel(logging.WARN)
if 'ERR' in loglevel_str.upper(): logging.getLogger().setLevel(logging.ERROR)
if 'CRI' in loglevel_str.upper(): logging.getLogger().setLevel(logging.CRITICAL)

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
    'exit': None, 'quit': None                                        # exit
})

session = Session(config)
network_mgr = NetworkManager(session = session)

availability_status = 'available'
def bottom_toolbar():
    # TODO future file data transfer progress (like the pipenv bar)
    # TODO video sent/received packets + bytes + frames + bitrate + etc...
    return prompt_toolkit.HTML(session.connection_status.getDescription() + '/ <b>' + availability_status + '</b> / (Press ctrl+d to exit)')

async def userprompt():
    commands = {}
    dummy = Call(commands, config, session, network_mgr)
    dummy = Hangup(commands, config, session, network_mgr)
    dummy = Say(commands, config, session, network_mgr)
    dummy = Login(commands, config, session, network_mgr)
    dummy = Logout(commands, config, session, network_mgr)
    dummy = Quit(commands, config, session, network_mgr)
    dummy = Lookup(commands, config, session, network_mgr)
    # TODO load all the commands availble from the commands folder vs manually like above (also loop import classes)

    prompt_session = PromptSession(
        completer=better_completer, bottom_toolbar=bottom_toolbar)

    while True:
        try:
            text = await prompt_session.prompt_async('> ')

            if not text:
                continue
            else:
                input_cmd_split = text.split()
            input_cmd_name, input_cmd_args = input_cmd_split[0], input_cmd_split[1:]

            command = commands.get(input_cmd_name) or None
            if not command:
                printf(f'<error>Unsupported command</error> {input_cmd_name}')
                continue

            show_help = False
            for arg in input_cmd_args:  # common args processing done here (versus in every command)
                if arg == '-h':
                    show_help = True
                    break

            if show_help:
                command.show_help()
            else:
                await command.do_command(*input_cmd_args)
        
            await asyncio.sleep(0)

        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        except Exception as e:
            traceback.print_exc()
    print('GoodBye!')

async def networktick():
    while True:
        if network_mgr.is_connected(): await network_mgr.tick()
        await asyncio.sleep(0)

@network_mgr.pc.on('track')
def on_track(track):
    logging.debug('Receiving %s' % track.kind)
    if track.kind == 'video':
        network_mgr.recorder.addTrack(videotransformtrack.VideoTransformTrack(network_mgr.remote_relay.subscribe(track)))
    # TODO: play audio track if present
    
if __name__ == '__main__':
    networktick = asyncio.get_event_loop().create_task(networktick())
    prompt = asyncio.get_event_loop().create_task(userprompt())
    asyncio.get_event_loop().run_forever()