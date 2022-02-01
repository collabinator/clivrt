import logging
from attrs import define
import websockets
import json
import asyncio
from configparser import ConfigParser
from datetime import datetime
from time import sleep
from cli import printf
from cli.datamodel.session import Session
from aiortc import RTCPeerConnection
from aiortc.sdp import candidate_from_sdp
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder, MediaRelay
from aiortc.contrib.signaling import BYE, object_to_string  ## TODO is this needed?
from prodict import Prodict

@define
class NetworkManager:
    session: Session = None
    config: ConfigParser = None

    # Websocket client
    wsclient: websockets.WebSocketClientProtocol = None

    # RTC peering
    local_relay = MediaRelay()  # my webcam
    remote_relay = MediaRelay() # incoming video
    pc = RTCPeerConnection() # TODO: Add STUN Servers to pc
    recorder = MediaBlackhole()

    async def tick(self):
        if self.wsclient is None: return
        if self.wsclient.open is not True: return
        try:
            message = await asyncio.wait_for(self.wsclient.recv(), timeout = 0.5) # wrapped in wait to avoid blocking 
            if message: await self.process_incoming(message)
        except websockets.ConnectionClosedError as e:
            logging.error('exception trying receive websocket message')
            logging.error(e)
            printf(f'<error>Lost connection to websocket - but it should reconnect</error>')
            return
        except TimeoutError as e:
            logging.debug('timeout waiting on websocket but that is OK')
            return
        except Exception as e:
            # something is triggering an empty exception?! 2022-01-30 hide for now
            # logging.error('exception in network tick')
            # logging.error(e)
            # printf(f'<error>Unknown websocket connection error</error>')
            return

    def is_connected(self):
        if self.wsclient is None: return False
        return self.wsclient.open

    async def connect_to_signaling_server(self, uri: str, my_username: str):
        if self.wsclient is not None:
            logging.warning('trying to connect to server but already connected to ' + self.wsclient.remote_address)
            # TODO should we force a disconnect?
        try:
            # for now the endpoint is /chat/yourusername (I think the server expects this TBD)
            self.wsclient = await websockets.connect(uri + '/chat/' + my_username)
            logging.debug('connected to websocket server')
        except Exception as e:
            logging.error('exception trying to open websocket to signaling server at: ' + uri + '/chat/' + my_username)
            logging.error(e)
            printf(f'<error>Connection to chat server failed</error>')
            return

    async def disconnect_from_signaling_server(self):
        if self.wsclient is None:
            logging.warning('cant disconnect because there is no active socket connection')
            return
        else:
            try:
                await self.wsclient.close()
                self.wsclient = None
                sleep(1)
                logging.debug('WebSocketApp connection closed')
            except Exception as e:
                logging.error('logout failed')
                logging.error(e)
                printf(f'<error>Could not logout from chat server</error>')
                return
    
    async def broadcast_message(self, message: str):
        logging.debug('broadcasting message: ' + message)
        try:
            msg_data = {
                'text': message,
                'type': 'message',
                'id': self.session.my_signaling_id,  # TODO get from server?
                'date': str(datetime.now())
            }
            await self.wsclient.send(json.dumps(msg_data))
        except Exception as e:
            logging.error('send failed')
            logging.error(e)
            printf(f'<error>Could not send chat message</error>')
            return

    async def process_incoming(self, message: str):
        msg_data = None
        type: str = 'unknown'
        try:
            msg_data = Prodict.from_dict(json.loads(message))
            type = msg_data['type']
            # TODO if target isnt me should we ignore?
        except Exception as e:
            logging.error('bad message data - could not parse')
            logging.error(e)
            return
        if type == 'userlist':
            await self.handle_msg_userlist(msg_data)
        elif type == 'message':
            await self.handle_msg_chat(msg_data)
        elif type == 'video-offer':
            await self.handle_msg_video_offer(msg_data)
        elif type == 'video-answer':
            await self.handle_msg_video_answer(msg_data)
        elif type == 'new-ice-candidate':
            await self.handle_msg_ice_candidate(msg_data)
        else:
            logging.warning('Could not process unsupported message type')

    async def handle_msg_userlist(self, msg_data):
        logging.debug('got userlist')
        try:
            users = msg_data['users']
            self.session.users_list.update_available(users)
        except Exception as e:
            logging.error('bad message data - could not parse userlist')
            logging.error(e)
            return

    async def handle_msg_chat(self, msg_data):
        logging.debug('got chat message')
        try:
            name = msg_data['name']
            text = msg_data['text']
            # TODO move chat off into a side panel on it's own
            printf(f'<chat><b>{name}</b>: <i>{text}</i></chat>')
        except Exception as e:
            logging.error('bad message data - could not parse chat message')
            logging.error(e)
            return

    async def handle_msg_video_offer(self, msg_data):
        logging.debug('got video offer message')
        # logging.debug(msg_data)
        try:
            name = msg_data['name']
            target = msg_data['target']
            logging.debug('processing video offer message for ' + target + ' from ' + name)
            await self.pc.setRemoteDescription(msg_data['sdp'])
            logging.debug('starting recorder and adding my webcam video track')
            await self.recorder.start()
            self.add_media_tracks()
            await self.pc.setLocalDescription(await self.pc.createAnswer())
            msg_data = {
                'sdp': json.loads(object_to_string(self.pc.localDescription)),
                'target': name,
                'type': 'video-answer',
                'name': self.session.my_name, # target should == my_name
                'date': str(datetime.now())
            }
            await self.wsclient.send(json.dumps(msg_data))
        except Exception as e:
            logging.error('bad message data - could not parse video offer message')
            logging.error(e)
            return

    async def handle_msg_video_answer(self, msg_data):
        logging.debug('got video answer message')
        try:
            name = msg_data['name']
            target = msg_data['target']
            logging.debug('processing video answer message for ' + target + ' from ' + name)
            msg_obj = Prodict.from_dict(json.loads(msg_data))
            await self.pc.setRemoteDescription(msg_obj['sdp'])
            await self.recorder.start()
        except Exception as e:
            logging.error('bad message data - could not parse video answer message')
            logging.error(e)
            return

    async def handle_msg_ice_candidate(self, msg_data):
        logging.debug('got ICE candidate message')
        try:
            name = msg_data['name']
            target = msg_data['target']
            logging.debug('processing ICE candidate message for ' + target + ' from ' + name)
            candidate = candidate_from_sdp(msg_data['candidate']['candidate'].split(':', 1)[1])
            candidate.sdpMid =  msg_data["candidate"]["sdpMid"]
            candidate.sdpMLineIndex = msg_data["candidate"]["sdpMLineIndex"]
            await self.pc.addIceCandidate(candidate)
        except Exception as e:
            logging.error('bad message data - could not parse ICE candiate message')
            logging.error(e)
            return

    async def invite_user_to_rtc(self, username: str):
        logging.debug('inviting a user to real time video chat')
        self.add_media_tracks()
        await self.pc.setLocalDescription(await self.pc.createOffer())
        msg_data = {
            'sdp': json.loads(object_to_string(self.pc.localDescription)),
            'target': username,
            'type': 'video-offer',
            'name': self.session.my_name,
            'date': str(datetime.now())
        }
        await self.wsclient.send(json.dumps(msg_data))

    async def end_rtc(self):
        logging.debug('sending hangup message to signaling server but stay connected')
        await self.recorder.stop()
        await self.pc.close()
        # self.wsclient.send(json.dumps(msg_data)) # is there some RTC message to send?
        # TODO clear tracks?
        # TODO local_relay unsubscribe?
        # TODO remote_relay anything?

    def add_media_tracks(self):
        framerate = self.config.defaults().get('framerate', '30')
        video_size = self.config.defaults().get('video_size', '640x480')
        try:
            options = {'framerate': framerate, video_size: '640x480'}
            if self.session.os_type == 'Darwin':
                webcam = MediaPlayer('default:none', format='avfoundation', options=options)
            elif self.session.os_type == 'Windows':
                webcam = MediaPlayer('video=Integrated Camera', format='dshow', options=options)
            else:
                webcam = MediaPlayer('/dev/video0', format='v4l2', options=options)
            self.pc.addTrack(self.local_relay.subscribe(webcam.video))
            # TODO: Add microphone track
        except Exception as e:
            logging.error('media issue - could not add local tracks')
            logging.error(e)
            return
