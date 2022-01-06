from attrs import asdict, define, make_class, Factory
import json
import logging

@define
class UsersList:
    available_users: list[str] = Factory(list)

    def update_available(self, users:str):
        try:
            logging.debug(users)
            self.available_users = users
        except Exception as e:
            logging.error('update user list failed')
            logging.error(e)
            return
