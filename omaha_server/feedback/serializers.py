# coding: utf8

"""
This software is licensed under the Apache 2 license, quoted below.

Copyright 2015 Crystalnix Limited

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

from feedback.models import Feedback


__all__ = ['FeedbackSerializer']


class FeedbackSerializer(serializers.HyperlinkedModelSerializer):
    feedback_data = serializers.DictField()

    class Meta:
        model = Feedback
        fields = ('id', 'created', 'modified',
                  'screenshot', 'blackbox', 'system_logs', 'attached_file',
                  'feedback_data')
