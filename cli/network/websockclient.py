import logging
from attrs import define
import websocket
import ssl
import threading
import json
from datetime import datetime
from time import sleep

#websocket.enableTrace(True)
websocket.setdefaulttimeout(30) # quick fix here, TODO move this into configurable options
@define
class WebSockClient:
    wsapp: websocket.WebSocketApp = None
    thread: threading.Thread = None

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
        logging.debug(message)

    def connect_to_signaling_server(self, uri: str, my_username: str):
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
