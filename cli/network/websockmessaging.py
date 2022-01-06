import logging
from re import M
from attrs import define
import json
from datetime import datetime
from cli.datamodel.session import Session
from cli import printf

@define
class WebSockMessaging:
    @classmethod
    def process_incoming(self, message: str, session: Session):
        msg_data = None
        type: str = 'unknown'
        try:
            msg_data = json.loads(message)
            type = msg_data['type']  
        except Exception as e:
            logging.error('bad message data - could not parse')
            logging.error(e)
            return
        
        if type == 'userlist':
            self.handle_msg_userlist(msg_data, session)
        elif type == 'message':
            self.handle_msg_chat(msg_data, session)
        elif type == 'video-offer':
            self.handle_msg_video_offer(msg_data, session)
        elif type == 'new-ice-candidate':
            self.handle_msg_ice_candidate(msg_data, session)
        else:
            logging.warning('Could not process unsupported message type')

    @classmethod
    def handle_msg_userlist(self, msg_data, session: Session):
        logging.debug('processing userlist')
        try:
            users = msg_data['users']
            session.users_list.update_available(users)
        except Exception as e:
            logging.error('bad message data - could not parse userlist')
            logging.error(e)
            return

    @classmethod
    def handle_msg_chat(self, msg_data, session: Session):
        logging.debug('processing chat message')
        try:
            name = msg_data['name']
            text = msg_data['text']
            printf(f'<b>{name}</b>: <i>{text}</i>')
        except Exception as e:
            logging.error('bad message data - could not parse chat message')
            logging.error(e)
            return

    @classmethod
    def handle_msg_video_offer(self, msg_data, session: Session):
        logging.debug('processing video offer message')
        try:
            name = msg_data['name']
            target = msg_data['target']
            sdp = msg_data['sdp']
            # TODO do something
        except Exception as e:
            logging.error('bad message data - could not parse video offer message')
            logging.error(e)
            return

    @classmethod
    def handle_msg_ice_candidate(self, msg_data, session: Session):
        logging.debug('processing ICE candidate message')
        try:
            name = msg_data['name']
            target = msg_data['target']
            candidate = msg_data['candidate']
        except Exception as e:
            logging.error('bad message data - could not parse ICE candiate message')
            logging.error(e)
            return