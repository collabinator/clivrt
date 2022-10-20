import configparser
import traceback
import logging
import asyncio
import io
import IPython.display as ipd
import grpc
import riva.client
import prompt_toolkit
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter, NestedCompleter
from prompt_toolkit.shortcuts.prompt import prompt
from prompt_toolkit.styles import Style
# TODO Will use these soon to split the screen into sections
# from prompt_toolkit.application import Application
# from prompt_toolkit.layout.containers import HSplit, VSplit, Window, WindowAlign
# from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
# from prompt_toolkit.layout.layout import Layout
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
network_mgr = NetworkManager(session=session, config=config)

# NVIDIA RIVA setup here (might need to move into the network folder and a custom class)
asr_on = config.defaults().get('asr_on', 'false')
riva_asr = None
if asr_on.lower() == 'true':
    riva_host_uri = config.defaults().get('asr_hosturl', 'localhost:50051')
    logging.debug(f'Setting up connection to RIVA server text captions, host=' + riva_host_uri)
    auth = riva.client.Auth(uri=riva_host_uri)
    riva_asr = riva.client.ASRService(auth)
    session.riva_connection.status = session.riva_connection.status.CONNECTED

tbstyle = Style.from_dict({
    'bottom-toolbar': '#33475b bg:#ffffff',
})
def bottom_toolbar():
    # TODO future file data transfer progress (like the pipenv bar)
    # TODO debugging status - video sent/received packets + bytes + frames + bitrate + etc...
    signaling_status = '⛔'
    riva_status = ' '
    if network_mgr.is_connected(): 
        signaling_status = '📢 🔓'
        if network_mgr.wsclient.secure: signaling_status = '📢 🔒'
    if session.riva_connection is not None:
        riva_status = session.riva_connection.getDescription()
    # return prompt_toolkit.HTML(
    return [('class:bottom-toolbar',
        session.connection_status.getDescription() + \
        ' ▪️ ' + signaling_status + \
        ' ' + riva_status + \
        ' ▪️ (Press tab to autocomplete, ctrl+d to exit)')]

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
        completer=better_completer, bottom_toolbar=bottom_toolbar, style=tbstyle)

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

vidstyle = config.defaults().get('videostyle', 'just-ascii')

@network_mgr.pc.on('track')
def on_track(track):
    logging.debug('Receiving %s' % track.kind)
    if track.kind == 'video':
        videotransform = videotransformtrack.VideoTransformTrack(track=network_mgr.remote_relay.subscribe(track), config=config) # Create a 'proxy' around the video for transforming
        videotransform.ve.set_strategy(vidstyle)
        network_mgr.recorder.addTrack(videotransform)
    elif track.kind == 'audio':
        network_mgr.recorder.addTrack(track)
        #if asr_on: # TODO: play audio track if present and pass to RIVA if TTS is enabled

if __name__ == '__main__':
    networktick = asyncio.get_event_loop().create_task(networktick())
    prompt = asyncio.get_event_loop().create_task(userprompt())
    asyncio.get_event_loop().run_forever()