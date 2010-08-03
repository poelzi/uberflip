#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import pygame

# Import extra libs for device interaction

try:
    import osso
except:
    osso = None
import dbus
import dbus.service
import gobject
from dbus.mainloop.glib import DBusGMainLoop
import time as myTime

# import gtk stuff for dialogs

import pygtk
import gtk
import hildon

sys.path.append('\\flipclock')
from pygame import *
import ci_init as ci

# import ci_alarmNew as ci_alarm
# import ci_input

import ci_flip
import ci_eventsNew as ci_events
import ci_gfx
import ci_clock

# Import the config/preferences module

import ci_config

# Import mainloop event handlers

import ci_eventHandlers

# Import DBus service class

import ci_dbus

# Import DBus/AlarmD interface

try:
    import ci_alarmD
    import alarmdModule as alarmd
except ImportError:
    print 'disable alarmd support'
    ci_alarmD = None

# Import the device monitoring stuff

import ci_deviceMonitor

#############################################################################
#  Flip Clock MAEMO 0.2.1 Beta
#  21.00 - 03/30/2009
#
#   Developers:
#   Main Rants and gfx:     Ciro Ippolito
#           Debianizer:     Faheem Pervez
#        Military time:     Rob Williams/jolouis
# ........AlarmD/Dbus
# ........   Integration:........Rob Williams/jolouis
#     Misc and support:     Faheem Pervez, Plop, Jaffa, Harry Petas, Daperl
#                           TrueJournals, jolouis, Pstamos
#
#   qui si entra dolenti e pesanti qui si esce leggeri e contenti.
#############################################################################


def main():

    # Load the user config/preferences

    ci_config.loadPrefs()

    # Set clock theme(mode) to preferred one

    ci.fcmode = ci_config.preferences['theme']

    # Initialize Clock variables and display

    ci_clock.init_app()

    # check to see if we need to attempt to fix alarms

    if ci.cliOptions.fixAlarms == True:
        broken = ci_alarmD.findBrokenAlarms()

        if len(broken) > 0:
            dialog = hildon.Note('confirmation', (hildon.Window(),
                                 str(len(broken))
                                 + ' broken FlipClock alarms were found in AlarmD queue; Do you want to fix these now?'
                                 , gtk.STOCK_DIALOG_WARNING))
            dialog.set_button_texts('Yes', 'No')
            resp = dialog.run()
            dialog.destroy()

            if resp == gtk.RESPONSE_OK:
                fixedCount = 0
                for thisAlarm in broken:
                    status = ci_alarmD.clearFlipAlarm(thisAlarm['cookie'
                            ])
                    if status:
                        fixedCount = fixedCount + 1

                dialog = hildon.Note('information', (hildon.Window(),
                        str(fixedCount) + ' of ' + str(len(broken))
                        + ' broken FlipClock alarms were fixed!',
                        gtk.STOCK_DIALOG_INFO))
                dialog.set_button_texts('Cool Thanks!')
                resp = dialog.run()
                dialog.destroy()

    # now setup main loop
    # Okay, new idea... what about a gobject.MainLoop(), but with an idle callback to check for mouse events, and a timeout
    # to actually redraw the clock/etc.

    # Add the idle event callback

    gobject.idle_add(ci_eventHandlers.clockEventIdle)

    # Get the time until the next minute passes, and setup the drawClockEvent to be called at that point

    theTime = myTime.ctime()
    gobject.timeout_add((60 - int(str(theTime[17]) + str(theTime[18])))
                        * 1000, ci_eventHandlers.drawClockEvent)

    # Setup osso callbacks for device state........

    # ci.device.set_device_state_callback(ci_eventHandlers.deviceStateChangeEvent, system_inactivity=True, user_data=None)

    if osso:
        device = osso.DeviceState(ci.osso_c)
        try:
            device.set_device_state_callback(ci_eventHandlers.deviceStateChangeEvent,
                    system_inactivity=True, user_data=None)
        except:
            print 'Your osso lib has an issue, power management disabled...'

    # Bind DBUS handlers
    # ci.session_bus.add_signal_receiver(ci_eventHandlers.dbusRecieveAlarm, "triggerAlarm", "org.maemo.flipclock", "org.maemo", "/org/maemo/flipclock")
    # ci.session_bus.add_signal_receiver(ci_eventHandlers.dbusRecieveAlarm, dbus_interface="org.maemo.flipclock");

    # Register Flipclock D-Bus server (allows AlarmD/other apps to communicate and control the flipclock)

    name = dbus.service.BusName(ci.dbusSettings['interface'],
                                ci.session_bus)
    object = ci_dbus.flipServiceObj(ci.session_bus)

    testCond = {}
    testCond['dbus_interface'] = ci.dbusSettings['interface']

    # ci_alarmD.listAlarms(testCond)
    # ci_alarmD.listAlarms()

    # setup the charging/device monitor

    ci_deviceMonitor.BatteryMonitor()

    # damn you LABAUDIO

    gobject.timeout_add(100, ci_eventHandlers.checkForAlarm)

    # Finally, run the main loop now that we've established all handlers........

    ci.loop.run()

    print 'done main loop'


main()

# I CAN FLY!! ***************************************************************
#              .------.                                             (  |) )
#   \`. ,,,   (  zzzzz ). @@@           \`.\\\\           \`.1111   (  |` )
#    \ \  u\   ).-----'\ \@ <\           \ \"`-\           \ \1 o\  ( O|  )
#     \ \   ) /'        \ \@  >           \ \   ]           \ \   > /'---'
#      \ \ ||\           \ \@)-\           \ \ )=\           \ \ )^\
#       \ \  /            \ \@-'            \ \  _|           \ \  _)
#        \ \(              \ \\  __          \ \(              \ \(
#         \ \`------.       \ \`'  `.-.       \ \`----.-.       \ \`----.-.
#  ._ _    \ \   `.|_`.._    \ \       `.._    \ \       `.._    \ \       `.
#  \ ` `-.  \ \ `-.____\ `-.  \ \ `-.____\ `-.  \ \ `-.____\ `-.  \ \ `-.____
#  \\ \   \  \ \______\\\   \  \ \______\\\   \  \ \______\\\   \  \ \______\
#    \ \   \  \          \   \  \          \   \  \        \ \   \  \
#  -. . \\  \  \ -------. \`. \  \ -------. \_.'\  \ -------. \`. \  \ ------
#    \ \ \`. \_.\ \      \ \ `.\_.\ \      \ \ `.\__\ \      \ \ `.\_.\ \
#  _____\_\_(_.__\_\______\_\_(_.__\_\______\_\_<,-._\_\______\_\_(_.__\_\___

