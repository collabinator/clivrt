import logging
from attrs import define
import websockets
import json
import asyncio
from datetime import datetime
from time import sleep
from cli import printf
from cli.datamodel.session import Session
from cli.media import videotransformtrack
from aiortc import RTCPeerConnection
from aiortc.sdp import candidate_from_sdp
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder, MediaRelay
from aiortc.contrib.signaling import BYE, object_to_string  ## TODO is this needed?

@define
class NetworkManager:
    session: Session = None

    # Websocket client
    wsclient: websockets.WebSocketClientProtocol = None

    # RTC peering
    event_loop = asyncio.get_event_loop()
    local_relay = MediaRelay()
    remote_relay = MediaRelay()
    pc = RTCPeerConnection() # TODO: Add STUN Servers to pc
    recorder = MediaBlackhole()

    async def tick(self):
        if (self.wsclient is None): return
        async for message in self.wsclient:
            await self.process_incoming(message)

    def is_connected(self):
        if self.wsclient is None: return False
        return self.wsclient.open

    async def connect_to_signaling_server(self, uri: str, my_username: str):
        if self.wsclient is not None:
            logging.warning('trying to connect to server but already connected to ' + self.wsclient.remote_address)
            # TODO should we force a disconnect?
        try:
            self.wsclient = await websockets.connect(uri + '/chat/' + my_username)
        except Exception as e:
            logging.error('exepction trying to open websocket to signaling server')
            logging.error(e)
            return

    async def disconnect_from_signaling_server(self):
        if self.wsclient is None:
            logging.warning('cant disconnect because there is no active socket connection')
            return
        else:
            try:
                self.wsclient.close()
                self.wsclient = None
                sleep(1)
                logging.debug('WebSocketApp connection closed')
            except Exception as e:
                logging.error('logout failed')
                logging.error(e)
                return
    
    async def broadcast_message(self, message: str, session):
        logging.debug('broadcasting message: ' + message)
        try:
            msg_data = {
                'text': message,
                'type': 'message',
                'id': session.my_signaling_id,  # TODO get from server?
                'date': str(datetime.now())
            }
            await self.wsclient.send(json.dumps(msg_data))
        except Exception as e:
            logging.error('send failed')
            logging.error(e)
            return

    async def process_incoming(self, message: str):
        msg_data = None
        type: str = 'unknown'
        try:
            msg_data = json.loads(message)
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
            printf(f'<b>{name}</b>: <i>{text}</i>')
        except Exception as e:
            logging.error('bad message data - could not parse chat message')
            logging.error(e)
            return

    async def handle_msg_video_offer(self, msg_data):
        logging.debug('got video offer message')
        try:
            name = msg_data['name']
            target = msg_data['target']
            sdp = msg_data['sdp']
            logging.debug('processing video offer message for ' + target + ' from ' + name)
            self.pc.setRemoteDescription(sdp)
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
            self.wsclient.send(json.dumps(msg_data))
        except Exception as e:
            logging.error('bad message data - could not parse video offer message')
            logging.error(e)
            return

    async def handle_msg_video_answer(self, msg_data):
        logging.debug('got video answer message')
        try:
            name = msg_data['name']
            target = msg_data['target']
            sdp = msg_data['sdp']
            logging.debug('processing video answer message for ' + target + ' from ' + name)
            await self.pc.setRemoteDescription(sdp)
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
            candidate = msg_data['candidate']
            candidate = candidate_from_sdp(candidate['candidate'].split(':', 1)[1])
            candidate.sdpMid = candidate['sdpMid']
            candidate.sdpMLineIndex = candidate['sdpMLineIndex']
            await self.pc.addIceCandidate(candidate)
        except Exception as e:
            logging.error('bad message data - could not parse ICE candiate message')
            logging.error(e)
            return
    
    async def invite_user_to_rtc(self, username: str):
        logging.debug('this is where we kick off the ICE logic flow')
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
        self.recorder.stop()
        self.pc.close()
        # self.wsclient.send(json.dumps(msg_data)) # is there some RTC message to send?
        # TODO clear tracks?
        # TODO local_relay unsubscribe?
        # TODO remote_relay anything?

    def add_media_tracks(self):
        options = {'framerate': '30', 'video_size': '640x480'}  # TODO get from session or config
        if self.session.os_type == 'Darwin':
            webcam = MediaPlayer('default:none', format='avfoundation', options=options)
        elif self.session.os_type == 'Windows':
            webcam = MediaPlayer('video=Integrated Camera', format='dshow', options=options)
        else:
            webcam = MediaPlayer('/dev/video0', format='v4l2', options=options)
        self.pc.addTrack(self.local_relay.subscribe(webcam.video))
        # TODO: Add microphone track

    @pc.on('track')
    def on_track(self, track):
        logging.debug('Receiving %s' % track.kind)
        if track.kind == 'video':
            self.recorder.addTrack(videotransformtrack.VideoTransformTrack(self.remote_relay.subscribe(track)))
        # TODO: play audio track if present