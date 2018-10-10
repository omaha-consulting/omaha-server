# coding: utf8

"""
This software is licensed under the Apache 2 license, quoted below.

Copyright 2014 Crystalnix Limited

Licensed under the Apache License, Version 2.0 (the "License"); you may not
use this file except in compliance with the License. You may obtain a copy of
the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations under
the License.
"""

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


class AESGCMCipher(object):
    """Decrypt AESGCM encrypted data ."""

    def __init__(self, key):
        self.key = key
        self.iv = '0' * 12
        self.additional_data = ''

    def decrypt(self, data, additional_data=None):
        """Decrypt data."""
        additional_data = self.additional_data or additional_data
        tag = data[-16:]
        data = data[:-16]
        decryptor = Cipher(
            algorithms.AES(self.key),
            modes.GCM(self.iv, tag),
            backend=default_backend()
        ).decryptor()
        if additional_data:
            decryptor.authenticate_additional_data(additional_data)
        return decryptor.update(data) + decryptor.finalize()

    def encrypt(self, plaintext, additional_data=None):
        additional_data = self.additional_data or additional_data
        encryptor = Cipher(
            algorithms.AES(self.key),
            modes.GCM(self.iv),
            backend=default_backend()
        ).encryptor()
        if additional_data:
            encryptor.authenticate_additional_data(additional_data)
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        return (ciphertext, encryptor.tag)


class RSACipher(object):
    """Decrypt message with a private key."""

    def __init__(self, private_key):
        self.private_key = serialization.load_pem_private_key(
            private_key,
            password=None,
            backend=default_backend()
        )

    def decrypt(self, ciphertext):
        return self.private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

    def encrypt(self, message):
        return self.private_key.public_key().encrypt(
            message,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )