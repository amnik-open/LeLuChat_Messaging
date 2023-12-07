"""Define django channel consumer for websocket"""
import json
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from messaging.authorization import RemoteAuthentication
from persist_messaging.producer import MessageProducer


class ChatConsumer(WebsocketConsumer):
    """Define consumer for django channels"""

    def __init__(self):
        self.chat_group_name = None
        self.room = None
        self.user = AnonymousUser()
        super().__init__()

    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        if self.chat_group_name:
            async_to_sync(self.channel_layer.group_discard)(
                self.chat_group_name, self.channel_name
            )

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        close = False
        if text_data_json["type"].lower() == "authorization":
            self.room = self.scope["url_route"]["kwargs"]["uid"]
            token = text_data_json["token"]
            chat = text_data_json["chat"]
            self.user = RemoteAuthentication(gateway_url=settings.LELUCHAT_MESSAGE_GATEWAY,
                                             room=self.room, chat=chat,
                                             token=token).get_sender()
            if self.user.is_authenticated:
                self.chat_group_name = f"chat_{chat}"
                async_to_sync(self.channel_layer.group_add)(
                    self.chat_group_name, self.channel_name
                )
                message = "Authentication is successful"
            else:
                message = "Authentication is not successful"
                close = True
            self.send(text_data=json.dumps({
                'type': text_data_json["type"],
                'message': message
            }))
            if close:
                self.close()
        elif not self.user.is_authenticated:
            self.send(text_data=json.dumps({
                'type': "authorization",
                'message': "You are not authenticated"
            }))
        elif self.user.is_authenticated and text_data_json["type"] == "chat_message":
            message_info = {}
            producer = MessageProducer(sender=self.user)
            producer.produce(text=text_data_json['message'])
            message_info['message_data'] = self._message_data(text=text_data_json['message'])
            message_info['type'] = 'send_to_all'
            return_dict = {**message_info}
            async_to_sync(self.channel_layer.group_send)(
                self.chat_group_name,
                return_dict,
            )
        else:
            self.send(text_data=json.dumps({
                'message': "Your message is not supported"
            }))

    def _message_data(self, text):
        return str({'text': text, 'sender': self.user.info})

    def send_to_all(self, event):
        text_data_json = event.copy()
        self.send(
            text_data=json.dumps(
                text_data_json['message_data']
            )
        )
