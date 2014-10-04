# coding: utf8

from .utils import convert_version_string_to_int, convert_version_int_to_string


class Version(object):
    def __init__(self, string, number_bits):
        """
        Take in a verison string e.g. '3.0.1'
        Store it as a converted int
        """
        self.number_bits = number_bits
        self.internal_integer = convert_version_string_to_int(string, number_bits)

    def __unicode__(self):
        return unicode(convert_version_int_to_string(self.internal_integer, self.number_bits))

    def __str__(self):
        return self.__unicode__()

    def __repr__(self):
        return self.__unicode__()

    def __int__(self):
        return self.internal_integer

    def __eq__(self, other):
        if not other:
            return False  # we are obviously a valid Version, but 'other' isn't
        if isinstance(other, basestring):
            return self == Version(other, self.number_bits)
        else:
            return int(self) == int(other)