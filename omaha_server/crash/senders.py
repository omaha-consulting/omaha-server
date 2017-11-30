import logging

from django.conf import settings

from raven import Client
from celery import signature
from logstash import TCPLogstashHandler


class BaseSender(object):
    name = None
    client = None

    def send(self, message, extra={}, tags={}, sentry_data={}, crash_obj=None):
        pass


class SentrySender(BaseSender):
    name="Sentry"

    def __init__(self):
        self.client = Client(
            getattr(settings, 'RAVEN_DSN_STACKTRACE', None),
            name=getattr(settings, 'HOST_NAME', None),
            release=getattr(settings, 'APP_VERSION', None)
        )

    def send(self, message, extra={}, tags={}, sentry_data={}, crash_obj=None):
        event_id = self.client.capture(
            'raven.events.Message',
            message=message,
            extra=extra,
            tags=tags,
            data=sentry_data
        )
        signature("tasks.get_sentry_link", args=(crash_obj.pk, event_id)).apply_async(queue='private', countdown=1)


class ELKSender(BaseSender):
    name="ELK"
    handler = None

    def __init__(self):
        host = getattr(settings, 'LOGSTASH_HOST', None)
        port = getattr(settings, 'LOGSTASH_PORT', None)
        if host and port:
            self.handler = TCPLogstashHandler(host, int(port), version=1)
        else:
            logging.error("Logstash settings are not configured")

    def send(self, message, extra={}, tags={}, sentry_data={}, crash_obj=None):
        if self.handler:
            logger = self._prepare_logger()
            extra.update(tags)
            # We don't want "sentry.interfaces" as part of a field name.
            extra['exception'] = sentry_data['sentry.interfaces.Exception']
            # The "message" is actually a crash signature, not appropriate for the ELK "message" field.
            extra['signature'] = message
            # All ELK messages are expected to include logger_name.
            extra['logger_name'] = 'omahaserver'
            # Send message with logger.
            logger.info("Sparrow Crashes", extra=extra)
        else:
            logging.error("Logstash settings are not configured")

    def _prepare_logger(self):
        """It's a workaround.

        If we do it in __init__ then logger won't send messages to Logstash
        """
        logger = logging.getLogger('crash_sender')
        logger.setLevel(logging.INFO)
        logger.handlers = []
        logger.addHandler(self.handler)
        return logger


senders_dict = {
    "Sentry": SentrySender,
    "ELK": ELKSender,
}


def get_sender(tracker_name=None):
    if not tracker_name:
        tracker_name = getattr(settings, 'CRASH_TRACKER', 'Sentry')
    try:
        sender_class = senders_dict[tracker_name]
    except KeyError:
        raise KeyError("Unknown tracker, use one of %s" % senders_dict.keys())
    return sender_class()