#!/usr/bin/python
# -*- coding: utf-8 -*-
#####################################################################
# D-BUS Service Object
#
# By Rob Williams (jolouis) for the FlipClock project
# Provides the flipclock D-Bus service that listens for messages
# from AlarmD (or manual dbus calls) and reacts accordingly (i.e. triggering
# alarms, etc)
#
######################################################################

import ci_init as ci

# events module

import ci_eventsNew as ci_events

# Import the config module

import ci_config

# Import alarm module

import ci_alarmNew as ci_alarm

import gobject

import dbus
import dbus.service
import dbus.mainloop.glib


class flipServiceObj(dbus.service.Object):

    def __init__(self, conn,
                 object_path='/org/maemo/flipclock/controller'):
        dbus.service.Object.__init__(self, conn, object_path)

    # Signals get sent out, methods are exposed to be called.

    @dbus.service.signal('org.maemo.flipclock')
    def HelloSignal(self, message):

        # The signal is emitted when this method exits
        # You can have code here if you wish

        pass

    # @dbus.service.method('org.maemo.flipclock')
    # def emitHelloSignal(self):
    #    #you emit signals by calling the signal's skeleton method
    #    self.HelloSignal('Hello')
    #    return 'Signal emitted'

    # Expose the "triggerAlarm" method

    @dbus.service.method('org.maemo.flipclock')
    def triggerAlarm(self, alarm_cookie=None, alarm_index=-1):

        # Alarm was triggered!

        print 'Received alarm trigger'

        # Try to determine which alarm it is and handle it

        for thisAlarm in ci_config.alarms:
            if int(thisAlarm['alarm_index']) == int(alarm_index):

                # Found matching alarm!

                print 'found matching alarm, running'
                ci_alarm.handleAlarm(thisAlarm)

                break

        print 'done running alarm'
        print alarm_cookie

        # we'll try a simple mode switch first as a test
        # ci_events.clockbutton1()
        # ci.device.display_state_on();

        return 'true'
        self.HelloSignal('Ok')


