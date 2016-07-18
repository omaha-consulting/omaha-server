import logging
from hashlib import sha256

from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone

import pytz
from ecdsa import SigningKey
from ecdsa.util import sigencode_der

logger = logging.getLogger(__name__)


class CUP2Exception(Exception):
    pass


class TimezoneMiddleware(object):
    def process_request(self, request):
        tzname = request.session.get('django_timezone')
        if tzname:
            timezone.activate(pytz.timezone(tzname))
        else:
            timezone.deactivate()


class CUP2Middleware(object):
    """Support CUP2 protocol of Omaha Client.
    """

    def __init__(self):
        self.sk = {}
        # Loading signature keys to memory
        for keyid, private_key in settings.CUP_PEM_KEYS.iteritems():
            self.sk[keyid] = SigningKey.from_pem(open(private_key).read())

    def process_request(self, request):
        if getattr(settings, 'CUP_REQUEST_VALIDATION', False) and self.is_cup2_request(request):
            try:
                self.validate_cup2_request(request)
            except Exception as e:
                logger.error('%s: %s\nrequest:\n%s\n\n%s\n' % (e.__class__.__name__, e.message,
                                                               request.META, request.body))
                msg = b'<?xml version="1.0" encoding="utf-8"?><data><message>Bad Request</message></data>'
                return HttpResponse(msg, status=400, content_type="text/html; charset=utf-8")

    def process_response(self, request, response):
        if self.is_cup2_request(request) and response.status_code // 100 == 2:
            self.sign_cup2_response(request, response)

        return response

    @staticmethod
    def is_cup2_request(request):
        """Detects CUP2 request by passed cup2key parameter.
        """
        return request.GET.get('cup2key') is not None

    def validate_cup2_request(self, request):
        cup2key = request.GET.get('cup2key')
        cup2hreq = request.GET.get('cup2hreq')

        keyid, k = cup2key.split(':')
        if keyid not in self.sk.keys():
            raise CUP2Exception('There is no key with id %s' % keyid)

        request_hash = sha256(request.body).hexdigest()
        if cup2hreq and request_hash != cup2hreq:
            raise CUP2Exception('Bad request hash\n"%s" != "%s"' % (request_hash, cup2hreq))

    def sign_cup2_response(self, request, response):
        cup2key = request.GET.get('cup2key')

        request_hash = sha256(request.body).digest()
        response_hash = sha256(response.content).digest()

        keyid, k = cup2key.split(':')
        # hash( hash(request) | hash(response) | cup2key )
        message = sha256(request_hash + response_hash + cup2key.encode()).digest()
        signature = self.sk[keyid].sign(message, hashfunc=sha256, sigencode=sigencode_der, k=int(k))

        response['ETag'] = '%s:%s' % (signature.encode('hex'), request_hash.encode('hex'))
