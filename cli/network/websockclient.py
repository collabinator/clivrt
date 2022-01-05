import logging
import json
from attrs import define
import websocket
import ssl
from cli.datamodel.connectionstatus import ConnectionStatus

#websocket.enableTrace(True)

@define
class WebSockClient:
    wsapp: websocket.WebSocketApp = None

    def broadcast_message(self, message: str):
        logging.debug('broadcasting message: ' + message)
        try:
            msg_data = {
                'text': message,
                'type': 'message',
                'id': '' 
            }
            self.wsapp.send(message)
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
        print(message)

    def connectToSignalingServer(self, uri: str, my_username: str):
        if self.wsapp is not None:
            logging.warning('trying to connect to server but already connected to ' + self.wsapp.url)
            return # is this the correct behavior?
        self.wsapp = websocket.WebSocketApp(uri + '/chat/' + my_username,
            on_message=self.on_message, on_error=self.on_error, on_open=self.on_open, on_close=self.on_close)
        logging.warning('websocket connection is allowing SSL to be invalid!')
        self.wsapp.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        return

    def inviteUserToRTC(self, username: str):
        logging.warning("TODO this is where we kick off the ICE logic flow")
        ### TODO ####

    def endRTC(self):
        logging.warning("TODO send hangup message to signaling server but stay connected")

    def disconnect(self):
        if self.wsapp is None:
            logging.warning('cant disconnect because there is no active socket connection')
            return
        else:
            try:
                self.wsapp.close()
                self.wsapp = None
                logging.debug('WebSocketApp connection closed')
            except Exception as e:
                logging.error('send failed')
                logging.error(e)
                return
