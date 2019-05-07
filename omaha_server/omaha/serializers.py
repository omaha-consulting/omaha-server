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
from django.utils import timezone

from rest_framework import serializers
from dateutil import parser
import pytz

from omaha.models import Application, Platform, Channel, Version, Action, Data, PartialUpdate


__all__ = ['AppSerializer', 'PlatformSerializer', 'ChannelSerializer', 'VersionSerializer']


class TimeZoneAwareDateTimeField(serializers.DateTimeField):
    def to_internal_value(self, value):
        local_dt = parser.parse(value)
        if not local_dt.tzinfo:
            tz = timezone.get_current_timezone()
            local_dt = tz.localize(local_dt)
        utc_dt = local_dt.astimezone(pytz.utc)
        return utc_dt


class DataSerializer(serializers.HyperlinkedModelSerializer):
    app = serializers.PrimaryKeyRelatedField(queryset=Application.objects.all())

    class Meta:
        model = Data
        fields = ('id', 'app', 'index', 'name', 'value')


class AppSerializer(serializers.HyperlinkedModelSerializer):
    data_set = DataSerializer(many=True, required=False, read_only=True)

    class Meta:
        model = Application
        fields = ('id', 'name', 'data_set')


class PlatformSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Platform
        fields = ('id', 'name')


class ChannelSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Channel
        fields = ('id', 'name')


class ActionSerializer(serializers.HyperlinkedModelSerializer):
    version = serializers.PrimaryKeyRelatedField(queryset=Version.objects.all())

    class Meta:
        model = Action
        fields = ('id', 'version', 'event', 'run', 'arguments', 'successurl',
                  'terminateallbrowsers', 'successsaction', 'other')


class VersionSerializer(serializers.HyperlinkedModelSerializer):
    is_enabled = serializers.BooleanField(default=True, required=False)
    app = serializers.PrimaryKeyRelatedField(queryset=Application.objects.all())
    platform = serializers.PrimaryKeyRelatedField(queryset=Platform.objects.all())
    channel = serializers.PrimaryKeyRelatedField(queryset=Channel.objects.all())
    version = serializers.CharField()

    class Meta:
        model = Version
        fields = ('id', 'is_enabled', 'is_critical', 'app', 'platform', 'channel',
                  'version', 'release_notes', 'file', 'file_hash', 'file_size',
                  'created', 'modified')
        read_only_fields = ('created', 'modified')

    def create(self, validated_data):
        if not validated_data.get('file_size'):
            file = validated_data['file']
            validated_data['file_size'] = file.size
        return super(VersionSerializer, self).create(validated_data)


class StatisticsMonthsSerializer(serializers.Serializer):
    data = serializers.DictField()


class MonthRangeSerializer(serializers.Serializer):
    start = serializers.DateTimeField(input_formats=['%Y-%m'], required=False)
    end = serializers.DateTimeField(input_formats=['%Y-%m'], required=False)


class MonthInputSerializer(serializers.Serializer):
    date = serializers.DateTimeField(input_formats=['%Y-%m'], required=False)


class LiveStatisticsInputSerializer(serializers.Serializer):
    start = TimeZoneAwareDateTimeField(required=False)
    end = TimeZoneAwareDateTimeField(required=False)
    channel = serializers.CharField(required=False)


class ServerVersionSerializer(serializers.Serializer):
    version = serializers.CharField()


class PartialUpdateSerializer(serializers.ModelSerializer):
    version = serializers.PrimaryKeyRelatedField(queryset=Version.objects.all())

    class Meta:
        model = PartialUpdate
        fields = '__all__'
