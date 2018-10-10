from django.test import TestCase

from ..ciphers import RSACipher, AESGCMCipher
from ..models import GeneratedKey

class RSACipherTest(TestCase):
    def test_encrypt_decrypt(self):
        key = GeneratedKey.generate()
        msg = '603deb1015ca71be2b73aef08577811f'
        cipher = RSACipher(key.private_key)
        ciphertext = cipher.encrypt(msg)
        decrypted_text = cipher.decrypt(ciphertext)
        assert decrypted_text == msg


class AESGCMCipherTest(TestCase):
    def test_encrypt_decrypt(self):
        key = '603deb1015ca71be2b73aef08577811f'
        aes_cipher = AESGCMCipher(key)
        message = 'test'
        ciphertext = ''.join(aes_cipher.encrypt(message))
        decrypted_text = aes_cipher.decrypt(ciphertext)
        assert decrypted_text == message
