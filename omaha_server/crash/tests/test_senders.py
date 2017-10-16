from django.test import TestCase

from omaha.tests.utils import temporary_media_root
from ..senders import get_sender, ELKSender, SentrySender


class GetSenderTest(TestCase):

    def test_default_sender(self):
        sender = get_sender()
        self.assertIsInstance(sender, SentrySender)

    @temporary_media_root(
        CRASH_TRACKER='ELK'
    )
    def test_elk_sender(self):
        sender = get_sender()
        self.assertIsInstance(sender, ELKSender)
