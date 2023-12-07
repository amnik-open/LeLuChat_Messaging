"""Define producer for messaging"""
import pika
import json
from persist_messaging.channel_connection import rabbit_connect

class MessageProducer:
    """Class to produce messages for leluchat_arsenal"""

    def __init__(self, sender):
        self.connection = rabbit_connect()
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='leluchat.arsenal.messaging', durable=True)
        self.sender = sender

    def _create_message(self, text):
        return {'sender': self.sender.info, 'text': text, 'chat': {'chat_uuid': self.sender.chat}}

    def produce(self, text):
        message = json.dumps(self._create_message(text))
        self.channel.basic_publish(exchange='',
                              routing_key='leluchat.arsenal.messaging',
                              body=message,
                              properties=pika.BasicProperties(
                                  delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                              ))
        self.connection.close()
