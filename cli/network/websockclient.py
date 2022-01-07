import logging
from aiortc.mediastreams import MediaStreamTrack
from attrs import define
import websocket
import ssl
import threading
import json
import cv2
import os
import sys
from datetime import datetime
from time import sleep
from prodict import Prodict

from cli.datamodel.connectionstatus import ConnectionStatusEnum
from cli.network.video_ascii import VideoTransformTrack
from cli.network.flag import FlagVideoStreamTrack

import argparse
import asyncio
import logging
import time

from video_to_ascii import video_engine

from aiortc import RTCIceCandidate, RTCPeerConnection, RTCSessionDescription, sdp, VideoStreamTrack
from aiortc.contrib.signaling import BYE, add_signaling_arguments, create_signaling, object_from_string, object_to_string, candidate_from_sdp
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder, MediaRelay

ROOT = os.path.dirname(__file__)
#websocket.enableTrace(True)
websocket.setdefaulttimeout(300) # quick fix here, TODO move this into configurable options
pc: RTCPeerConnection = RTCPeerConnection()
relay = MediaRelay()
recorder = MediaBlackhole()

class VideoTransformTrack(MediaStreamTrack):
    """
    A video stream track that transforms frames from an another track.
    """

    kind = "video"

    def __init__(self, track):
        super().__init__()
        self.track = track

    async def recv(self):
        frame = await self.track.recv()

        ve = video_engine.VideoEngine("just-ascii")
        ve.render_strategy.render_frame(frame.to_ndarray(format="bgr24"))
        
        return frame

@define
class WebSockClient:
    my_username: str = "test"
    wsapp: websocket.WebSocketApp = None
    thread: threading.Thread = None

    @pc.on("track")
    async def on_track(track):
        if track.kind == "video":
            await recorder.start()
            recorder.addTrack(VideoTransformTrack(relay.subscribe(track)))
            

    def is_connected(self):
        if self.wsapp is None: return False
        return self.wsapp.sock.connected

    def broadcast_message(self, message: str, session):
        logging.debug('broadcasting message: ' + message)
        try:
            msg_data = {
                'text': message,
                'type': 'message',
                'id': session.my_signaling_id,  # TODO get from server?
                'date': str(datetime.now())
            }
            self.wsapp.send(json.dumps(msg_data))
        except Exception as e:
            logging.error('send failed')
            logging.error(e)
            return

    def on_close(self, wsapp, close_status_code, close_msg):
        logging.debug('on_close args:')         # Because on_close was triggered, we know the opcode = 8
        if close_status_code or close_msg:
            logging.debug('close status code: ' + str(close_status_code))
            logging.debug('close message: ' + str(close_msg))

    def on_open(self, wsapp):
        logging.debug('socket opened')

    def on_error(self, wsapp, error: Exception):
        logging.error('websocket on_error: got exception ' + type(error).__name__ + ' details follow...')
        logging.error(error)

    def on_message(self, wsapp, message):
        logging.debug('got a message')
        msg_obj = Prodict.from_dict(json.loads(message))
        if msg_obj['type'] == 'video-offer':
            asyncio.run(pc.setRemoteDescription(msg_obj['sdp']))

            pc.addTrack(FlagVideoStreamTrack())

            asyncio.run(pc.setLocalDescription(asyncio.run(pc.createAnswer())))
            msg_data = {
                'sdp': json.loads(object_to_string(pc.localDescription)),
                'target': msg_obj['name'],
                'type': 'video-answer',
                'name': self.my_username,
                'date': str(datetime.now())
            }
            self.wsapp.send(json.dumps(msg_data))
        elif msg_obj['type'] == 'new-ice-candidate':
            candidate = candidate_from_sdp(msg_obj["candidate"]["candidate"].split(":", 1)[1])
            candidate.sdpMid = msg_obj["candidate"]["sdpMid"]
            candidate.sdpMLineIndex = msg_obj["candidate"]["sdpMLineIndex"]
            asyncio.run(pc.addIceCandidate(candidate))
        else:
            logging.debug(message)


    def connect_to_signaling_server(self, uri: str, my_username: str):
        self.my_username = my_username
        if self.wsapp is not None:
            logging.warning('trying to connect to server but already connected to ' + self.wsapp.url)
            return # is this the correct behavior?
        try:
            def ws_runloop():
                logging.debug('starting websocket thread run loop')
                self.wsapp.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
            self.wsapp = websocket.WebSocketApp(uri + '/chat/' + my_username,
                on_message=self.on_message, on_error=self.on_error, on_open=self.on_open, on_close=self.on_close)
            logging.warning('websocket connection is allowing SSL to be invalid!')
            thread = threading.Thread(target=ws_runloop)
            thread.daemon = True
            thread.start()
            logging.debug('main thread id: ' + str(threading.main_thread().ident) + '/started new thread id:' + str(thread.ident))
            self.session.connection_status.status = ConnectionStatusEnum.INGROUPCALL
        except Exception as e:
            logging.error('exepction trying to open websocket to signaling server')
            logging.error(e)
            return

    def invite_user_to_rtc(self, username: str):
        logging.warning("TODO this is where we kick off the ICE logic flow")
        ### TODO ####

    def end_rtc(self):
        logging.warning("TODO send hangup message to signaling server but stay connected")

    def disconnect(self):
        if self.wsapp is None:
            logging.warning('cant disconnect because there is no active socket connection')
            return
        else:
            try:
                self.wsapp.close()
                self.wsapp = None
                sleep(3)
                logging.debug('WebSocketApp connection closed')
            except Exception as e:
                logging.error('logout failed')
                logging.error(e)
                return
