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
import io
import os
import tarfile
import zipfile
import base64
from logging import getLogger

from cacheops import cached_as

from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from omaha_server.celery import app
from crash.models import Crash
from feedback.models import Feedback
from .models import GeneratedKey
from .ciphers import AESGCMCipher, RSACipher
from .fetchers import get_fetcher


logger = getLogger(__name__)

@app.task(name='tasks.generate_key')
def generate_key():
    GeneratedKey.generate()

blackbox_field_mapping = {
    Crash: 'archive',
    Feedback: 'blackbox'
}


@app.task(name='tasks.decrypt', ignore_result=True)
def decrypt(obj_pk, model_type):
    obj = model_type.objects.get(pk=obj_pk)
    if not obj.decryption_data:
        logger.warning("%s #%s hasn't decryption data" % (model_type.__name__, obj_pk))
        return
    blackbox_field = blackbox_field_mapping[model_type]
    blackbox_size_field = '%s_size' % blackbox_field
    obj_blackbox = getattr(obj, blackbox_field)
    blackbox_file, other_files, dat_name = untar(obj_blackbox)
    is_zipped = dat_name.endswith('.zip')
    if is_zipped:
        blackbox_file, zipped_dat_name = unzip(blackbox_file)

    decrypted_blackbox = decrypt_blackbox(blackbox_file.read(), obj.decryption_data)

    if is_zipped:
        data = zip_blackbox(zipped_dat_name, decrypted_blackbox)
    else:
        data = io.BytesIO(decrypted_blackbox)

    tarred_content = tar_blackbox(dat_name, data, other_files)
    update_bb_field(tarred_content, obj, blackbox_size_field, obj_blackbox)
    data.close()


def untar(obj_blackbox):
    t_file = tarfile.open(fileobj=obj_blackbox, mode='r')

    def is_blackbox_name(name):
        return name.endswith('.dat') or name.endswith('.dat.zip')

    dat_name = [x for x in t_file.getnames() if is_blackbox_name(x)][0]
    other_files = [x for x in t_file.getmembers() if not is_blackbox_name(x.name)]
    other_files = [(info, t_file.extractfile(info)) for info in other_files]
    blackbox_file = t_file.extractfile(dat_name)
    t_file.close()
    return blackbox_file, other_files, dat_name


def unzip(obj):
    with zipfile.ZipFile(io.BytesIO(obj.read())) as z_file:
        zipped_dat_name = [x for x in z_file.namelist()
                           if x.endswith('.dat')][0]
        return z_file.open(zipped_dat_name), zipped_dat_name


def zip_blackbox(zipped_dat_name, decrypted_blackbox):
    zipped_bb = io.BytesIO()
    zf = zipfile.ZipFile(zipped_bb, "w", zipfile.ZIP_DEFLATED)
    zf.writestr(zipped_dat_name, decrypted_blackbox)
    zf.close()
    zipped_bb.seek(0)
    return zipped_bb


def tar_blackbox(dat_name, data, other_files):
    tarred_content = io.BytesIO()
    tarred = tarfile.open(fileobj=tarred_content, mode='w')
    tarinfo = tarfile.TarInfo(dat_name)
    tarinfo.size = len(data.getvalue())
    tarred.addfile(tarinfo, fileobj=data)
    for info, content in other_files:
        tarred.addfile(info, content)
    tarred.close()
    tarred_content.seek(0)
    return tarred_content


def update_bb_field(tarred_content, obj, blackbox_size_field, obj_blackbox):
    wrapped_file = SimpleUploadedFile('1.tar', tarred_content.read())
    setattr(obj, blackbox_size_field, wrapped_file.size)
    obj_blackbox.save(os.path.basename(obj_blackbox.name), wrapped_file)
    obj.decryption_data.is_decrypted = True
    obj.decryption_data.save()
    wrapped_file.close()
    tarred_content.close()


def decrypt_blackbox(encrypted_blackbox, decryption_data):
    key_id = decryption_data.key_id
    encrypted_aes_key = base64.b64decode(decryption_data.encrypted_aes_key)
    private_key = get_cached_private_key(key_id)
    rsa_cipher = RSACipher(private_key)
    aes_key = rsa_cipher.decrypt(encrypted_aes_key)
    aes_cipher = AESGCMCipher(aes_key)
    blackbox = aes_cipher.decrypt(encrypted_blackbox)
    return blackbox

cache_timeout = settings.CACHE_TIMEOUT_SEC['private_key_by_hash']
@cached_as(GeneratedKey, timeout=cache_timeout)
def get_cached_private_key(key_id):
    fetcher = get_fetcher()
    return fetcher.get_private_key(key_id)
