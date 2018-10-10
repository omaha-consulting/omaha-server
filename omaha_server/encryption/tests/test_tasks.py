import io
import tarfile
import zipfile
from mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from ..factories import GeneratedKeyFactory, DecryptionDataFactory
from ..tasks import untar, unzip, tar_blackbox, zip_blackbox, decrypt_blackbox

User = get_user_model()

class DecryptionTest(TestCase):

    def test_tar_untar(self):
        content = 'dat content'
        filename = 'test.dat'
        t_file_content = tar_blackbox(filename, io.BytesIO(content), [])
        x = tarfile.TarFile(fileobj=t_file_content)
        assert x.getnames() == [filename]
        t_file_content.seek(0)
        blackbox_file, other_files, dat_name = untar(t_file_content)
        assert blackbox_file.read() == content
        assert other_files == []
        assert dat_name == filename

    def test_zip_unzip(self):
        content = 'dat content'
        filename = 'test.dat'
        data = zip_blackbox(filename, content)
        data.seek(0)
        zf = zipfile.ZipFile(data)
        assert zf.namelist() == [filename]
        data.seek(0)
        unzipped_file, unzipped_name = unzip(data)
        assert unzipped_file.read() == content
        assert unzipped_name == filename

    @patch('encryption.tasks.RSACipher', autospec=True)
    @patch('encryption.tasks.AESGCMCipher', autospec=True)
    def test_decrypt_blackbox(self, mock_aes, mock_rsa):
        mock_aes_decrypt = mock_aes.return_value.decrypt
        mock_rsa_decrypt = mock_rsa.return_value.decrypt
        decrypted_aes_key = 'decrypted_aes_key'
        mock_rsa_decrypt.return_value = decrypted_aes_key
        decryption_data = DecryptionDataFactory.create()
        blackbox = 'encrypted_text'
        decrypt_blackbox(blackbox, decryption_data)
        mock_rsa.assert_called_with(decryption_data.key.private_key)
        mock_rsa_decrypt.assert_called_once_with('some_key')
        mock_aes.assert_called_with(decrypted_aes_key)
        mock_aes_decrypt.assert_called_once_with(blackbox)
