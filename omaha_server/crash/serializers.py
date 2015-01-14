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

from rest_framework import serializers

from models import Symbols


__all__ = ['SymbolsSerializer']


class SymbolsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Symbols
        fields = ('id', 'file', 'debug_id', 'debug_file',
                  'created', 'modified')
        read_only_fields = ('created', 'modified')

    def _parse_debug_meta_info(self, head):
        head_list = head.split(' ')
        if head_list[0] != 'MODULE':
            raise serializers.ValidationError(u"The file contains invalid data.")
        return dict(debug_id=head_list[-2],
                    debug_file=head_list[-1])

    def create(self, validated_data):
        if not validated_data.get('debug_id') or \
                not validated_data.get('debug_file'):
            file = validated_data['file']
            try:
                head = file.readline().rstrip()
                meta = self._parse_debug_meta_info(head)
                validated_data.update(meta)
            except:
                raise serializers.ValidationError(u"The file contains invalid data.")
        return super(SymbolsSerializer, self).create(validated_data)
