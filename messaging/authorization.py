"""Utility for remote authentication class"""
import logging
import json
import requests
from django.contrib.auth.models import AnonymousUser

log = logging.getLogger(__name__)


class RemoteAuthentication:
    """Class to request gateway in leluchat_arsenal"""

    def __init__(self, gateway_url, token, room, chat):
        self.gateway_url = gateway_url
        self.token = token
        self.room = room
        self.chat = chat
    def _make_request(self):
        resp = requests.post(self.gateway_url, headers={"Authorization": self.token},
                             data={"room": self.room, "chat": self.chat})
        log.error(resp)
        resp.raise_for_status()
        return resp.json()

    def get_sender(self):
        try:
            return Sender(self._make_request(), self.room, self.chat)
        except Exception:
            return AnonymousUser()


class Sender:
    """Class representing sender of messages"""

    def __init__(self, data, room, chat):
        self.data = data
        self.room = room
        self.chat = chat

    @property
    def info(self):
        return json.loads(self.data)

    @property
    def room_uuid(self):
        return self.room

    @property
    def chat_uuid(self):
        return self.chat

    @property
    def is_authenticated(self):
        return True
