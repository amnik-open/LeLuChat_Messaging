"""Connect to rabbitmq"""
import pika
import logging
import time
from django.conf import settings

log = logging.getLogger(__name__)

def rabbit_connect():
    rabbitmq_conf = settings.RABBITMQ['default']
    credentials = pika.PlainCredentials(rabbitmq_conf['USER'], rabbitmq_conf['PASSWORD'])
    parameters = pika.ConnectionParameters(rabbitmq_conf['HOST'], rabbitmq_conf['PORT'],
                                           rabbitmq_conf['VIRTUAL_HOST'], credentials)
    retry = rabbitmq_conf['retry']
    wait = rabbitmq_conf['wait']
    connection = None
    exc = None
    while retry > 0:
        log.info("Try connecting to rabbitmq")
        try:
            connection = pika.BlockingConnection(parameters)
            break
        except Exception as e:
            log.exception(e)
            exc = e
        if exc:
            time.sleep(wait)
        retry -= 1
    if not connection:
        raise exc
    return connection
