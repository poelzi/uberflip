#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
This module implements gconf functionality on systems where the gconf Python
bindings are not available. It calls C{gconftool-2} instead.
@since: 0.96
"""

import commands

_GCONFTOOL = 'LANG=C gconftool-2'

VALUE_BOOL = 'bool'
VALUE_FLOAT = 'float'
VALUE_INT = 'int'
VALUE_LIST = 'list'
VALUE_PAIR = 'pair'
VALUE_STRING = 'string'


class _Client(object):

    def __init__(self):

        pass

    def get_without_default(self, key):

        return self.get_string(key)

    def get_list(self, key, ktype):

        (fail, out) = commands.getstatusoutput('%s --get %s'
                % (_GCONFTOOL, key))
        if fail:
            return None
        elif out.startswith('No value set for '):

            return None

        out = out.strip()
        out = out[1:-1]
        values = [v.strip() for v in out.split(',') if v]

        if ktype == VALUE_INT:
            values = [int(v) for v in values if v.isdigit()]

        return values

    def set_list(
        self,
        key,
        ktype,
        value,
        ):

        if ktype == VALUE_INT:
            value = [str(v) for v in value]
        s_value = ','.join(value)

        # print "%s --type list --list-type %s --set %s \"[%s]\"" \
        #                                    % (_GCONFTOOL, ktype, key, s_value)

        (fail, out) = \
            commands.getstatusoutput('%s --type list --list-type %s --set %s "[%s]"'
                 % (_GCONFTOOL, ktype, key, s_value))

        # print fail, out

    def get_string(self, key):

        (fail, out) = commands.getstatusoutput('%s --get %s'
                % (_GCONFTOOL, key))
        if fail:
            return None
        elif out.startswith('No value set for '):

            return None

        value = out.strip()

        return value

    def set_string(self, key, value):

        (fail, out) = \
            commands.getstatusoutput('%s --type %s --set %s "%s"'
                % (_GCONFTOOL, VALUE_STRING, key, value))

    def get_int(self, key):

        (fail, out) = commands.getstatusoutput('%s --get %s'
                % (_GCONFTOOL, key))
        if fail:
            return None
        elif out.startswith('No value set for '):

            return None

        value = out.strip()

        return int(value)

    def set_int(self, key, value):

        (fail, out) = \
            commands.getstatusoutput('%s --type %s --set %s "%s"'
                % (_GCONFTOOL, VALUE_INT, key, value))

    def get_bool(self, key):

        (fail, out) = commands.getstatusoutput('%s --get %s'
                % (_GCONFTOOL, key))
        if fail:
            return None
        elif out.startswith('No value set for '):

            return None

        value = out.strip()

        return bool(value)

    def set_bool(self, key, value):

        (fail, out) = \
            commands.getstatusoutput('%s --type %s --set %s "%s"'
                % (_GCONFTOOL, VALUE_BOOL, key, value))

    def unset(self, key):

        (fail, out) = commands.getstatusoutput('%s --unset %s'
                % (_GCONFTOOL, key))


_singleton = _Client()


def client_get_default():
    return _singleton


