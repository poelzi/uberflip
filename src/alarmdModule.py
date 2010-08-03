#!/usr/bin/python
# -*- coding: utf-8 -*-
# interface to the Nokia alarmd functions
#
# See <http://maemo.org/development/documentation/how-tos/3-x/howto_alarm_interface_bora.html>

version_long = 'Last Update: <22-OCT-2007 21:44:18>'

from ctypes import *

alarmd_lib = CDLL('libalarm.so.0')

###################################################################################################################
### errors & exceptions

# alarm_error_t enum

(
    ALARMD_SUCCESS,
    ALARMD_ERROR_DBUS,
    ALARMD_ERROR_CONNECTION,
    ALARMD_ERROR_INTERNAL,
    ALARMD_ERROR_MEMORY,
    ALARMD_ERROR_ARGUMENT,
    ) = range(6)

# corresponding exceptions


class Alarmd_Error(Exception):

    pass


class Alarmd_Error_DBUS(Alarmd_Error):

    pass


class Alarmd_Error_Connection(Alarmd_Error):

    pass


class Alarmd_Error_Internal(Alarmd_Error):

    pass


class Alarmd_Error_Memory(Alarmd_Error):

    pass


class Alarmd_Error_Argument(Alarmd_Error):

    pass


# check for errors after every call


def check_for_error():
    err = alarmd_lib.alarmd_get_error()
    print err
    if err != ALARMD_SUCCESS:
        if err == ALARMD_ERROR_DBUS:
            raise Alarmd_Error_DBUS
        elif err == ALARMD_ERROR_CONNECTION:
            raise Alarmd_Error_Connection
        elif err == ALARMD_ERROR_INTERNAL:
            raise Alarmd_Error_Internal
        elif err == ALARMD_ERROR_MEMORY:
            raise Alarmd_Error_Memory
        elif err == ALARMD_ERROR_ARGUMENT:
            raise Alarmd_Error_Argument
        else:

            # shouldn't happen...

            raise RuntimeError


###################################################################################################################
### structures & types

# typedef long cookie_t;

# typedef struct {
#         time_t alarm_time;
#         uint32_t recurrence;
#         int32_t recurrence_count;
#         uint32_t snooze;
#         char *title;
#         char *message;
#         char *sound;
#         char *icon;
#         char *dbus_interface;
#         char *dbus_service;
#         char *dbus_path;
#         char *dbus_name;
#         char *exec_name;
#         int32_t flags;
#         uint32_t snoozed;
# } alarm_event_t;


class alarm_event_t(Structure):

    _fields_ = [
        ('alarm_time', c_long),
        ('recurrence', c_uint32),
        ('recurrence_count', c_int32),
        ('snooze', c_uint32),
        ('title', c_char_p),
        ('message', c_char_p),
        ('sound', c_char_p),
        ('icon', c_char_p),
        ('dbus_interface', c_char_p),
        ('dbus_service', c_char_p),
        ('dbus_path', c_char_p),
        ('dbus_name', c_char_p),
        ('exec_name', c_char_p),
        ('flags', c_int32),
        ('snoozed', c_uint32),
        ]


alarm_event_t_p = POINTER(alarm_event_t)

###################################################################################################################
### set up function prototypes

### Test by Rob

# cookie_t *alarm_event_query(const time_t first, const time_t last, int32_t flag_mask, int32_t flags)

alarmd_lib.alarm_event_query.restype = POINTER(c_long)
alarmd_lib.alarm_event_query.argtypes = [c_ulonglong, c_ulonglong,
        c_int, c_int]

# cookie_t alarm_event_add(alarm_event_t *event)

alarmd_lib.alarm_event_add.restype = c_long
alarmd_lib.alarm_event_add.argtypes = [alarm_event_t_p]

# alarm_event_t *alarm_event_get(cookie_t event_cookie)

alarmd_lib.alarm_event_get.restype = alarm_event_t_p
alarmd_lib.alarm_event_get.argtypes = [c_long]

# void alarm_event_free(alarm_event_t *event)

alarmd_lib.alarm_event_free.restype = None
alarmd_lib.alarm_event_free.argtypes = [alarm_event_t_p]

# int alarm_event_del(cookie_t event_cookie)

alarmd_lib.alarm_event_del.restype = c_int
alarmd_lib.alarm_event_del.argtypes = [c_long]

# alarm_error_t alarmd_get_error(void)

alarmd_lib.alarmd_get_error.restype = c_int32

# char *alarm_escape_string(const char *string)

alarmd_lib.alarm_escape_string.restype = c_char_p
alarmd_lib.alarm_escape_string.argtypes = [c_char_p]

# char *alarm_unescape_string(const char *string)

alarmd_lib.alarm_unescape_string.restype = c_char_p
alarmd_lib.alarm_unescape_string.argtypes = [c_char_p]

# char *alarm_unescape_string_noalloc(char *string)

alarmd_lib.alarm_unescape_string_noalloc.restype = c_char_p
alarmd_lib.alarm_unescape_string_noalloc.argtypes = [c_char_p]

###################################################################################################################
### public functions for people to use

# alarmeventflags enum

ALARM_EVENT_NO_DIALOG = 1 << 0
ALARM_EVENT_NO_SNOOZE = 1 << 1
ALARM_EVENT_SYSTEM = 1 << 2
ALARM_EVENT_BOOT = 1 << 3
ALARM_EVENT_ACTDEAD = 1 << 4
ALARM_EVENT_SHOW_ICON = 1 << 5
ALARM_EVENT_RUN_DELAYED = 1 << 6
ALARM_EVENT_CONNECTED = 1 << 7
ALARM_EVENT_ACTIVATION = 1 << 8
ALARM_EVENT_POSTPONE_DELAYED = 1 << 9
ALARM_EVENT_BACK_RESCHEDULE = 1 << 10

# create an alarm


def add_alarm(
    alarm_time,
    recurrence,
    recurrence_count,
    snooze,
    title,
    message,
    sound,
    icon,
    dbus_interface,
    dbus_service,
    dbus_path,
    dbus_name,
    exec_name,
    flags,
    ):

    # set up structure

    arg = alarm_event_t()
    arg.alarm_time = int(alarm_time)
    arg.recurrence = recurrence
    arg.recurrence_count = recurrence_count
    arg.snooze = snooze
    arg.title = title
    arg.message = message
    arg.sound = sound
    arg.icon = icon
    arg.dbus_interface = dbus_interface
    arg.dbus_service = dbus_service
    arg.dbus_path = dbus_path
    arg.dbus_name = dbus_name
    arg.exec_name = exec_name
    arg.flags = flags

    # do the call

    cookie = alarmd_lib.alarm_event_add(byref(arg))
    if cookie == 0:
        check_for_error()
    return cookie


# get alarm info


def get_alarm(cookie):

    # do the call

    ptr = alarmd_lib.alarm_event_get(cookie)
    if not ptr:
        check_for_error()

    # save data to pass back

    alarm = ptr.contents
    v = {}
    v['cookie'] = int(cookie)
    v['alarm_time'] = alarm.alarm_time
    v['recurrence'] = alarm.recurrence
    v['recurrence_count'] = alarm.recurrence_count
    v['snooze'] = alarm.snooze
    v['title'] = alarm.title
    v['message'] = alarm.message
    v['sound'] = alarm.sound
    v['icon'] = alarm.icon
    v['dbus_interface'] = alarm.dbus_interface
    v['dbus_service'] = alarm.dbus_service
    v['dbus_path'] = alarm.dbus_path
    v['dbus_name'] = alarm.dbus_name
    v['exec_name'] = alarm.exec_name
    v['flags'] = alarm.flags
    v['snoozed'] = alarm.snoozed

    # now free alarm structure

    alarmd_lib.alarm_event_free(ptr)

    return v


# cancel an alarm


def cancel_alarm(cookie):

    # do the call - returns True on success

    return bool(alarmd_lib.alarm_event_del(cookie))


############# test Rob


def query_alarms(
    start_time,
    end_time,
    flags,
    flagMask,
    ):

    # try the call

    ptr = alarmd_lib.alarm_event_query(start_time, end_time, flags,
            flagMask)
    if not ptr:
        check_for_error()

    alarmList = ptr.contents


