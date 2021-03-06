#!/usr/bin/python
# -*- coding: utf-8 -*-
######################################################################
# Main FlipClock routines/callbacks.
# Setup in main application and executed by gobject.MainLoop()
# Rob Williams
# 20.00 02/27/2009
######################################################################

# Import libs that we need

try:
    import osso
except ImportError:
    osso = None
import dbus
import time as myTime
import sys
import gobject

# import gtk stuff for dialogs

import pygtk
import gtk
import hildon

import ci_init as ci
import ci_eventsNew as ci_events
import ci_flip
import ci_clock
import ci_alarmNew as ci_alarm
import ci_config

from pygame import *

# tracker for hold reset

defaultDownTime = 0

###############################################################################
# clockEventIdle
# This function gets called periodically by the mainloop
# whenever nothing is happening. It first checks for any
# pygame events that might be pending, and processes them.
# Once those are handled, it checks to see if the tablet is
# in "idle mode", and sleeps for either 10 ms or 100ms if idle
# (to try to save battery since response time is not as important)
# Finally, must return true in order to run in the next mainloop iteration
#
# NO CLOCK/TIME events here, just pygame interactivity events
###############################################################################


def clockEventIdle():
    global defaultDownTime

    # nothing else going on, so check for pygame events?...

    event = ci.pygame.event.poll()

    if event.type == QUIT:

        # Put the dim mode back if it was changed

        if ci.dimChanged == 1:
            ci_config.setAllNight(0)

        # Put the LED back to regular mode if present

        ci_alarm.setLEDMode('run')
        ci.pygame.display.quit
        ci.pygame.quit()
        ci.loop.quit()
    elif event.type == MOUSEBUTTONDOWN:

        ci_events.mouseDown = 1
        ci_events.tap_down()  # Check where the user tap/click
    elif event.type == MOUSEBUTTONUP:
        ci_events.mouseDown = 0
        ci_events.tap_release()  # User HAVE to release to s*it happen
    elif event.type == MOUSEMOTION:
        if ci_events.mouseDown:

            # Mouse is moving while pressing, so fire events

            ci_events.tap_drag()  # Mouse is being dragged while held down
    elif event.type == KEYUP:

        # Hardware key was pressed

        print event.key
        if event.key == 287:

            # fullscreen toggle button was pressed

            ci_events.toggleWindowMode()
        elif event.key == 27:

            # temporarily use "escape key" to toggle insomniac mode

            newMode = ci_config.setAllNight()

            osso_c = osso.Context('osso_test_note', '0.0.1', False)
            note = osso.SystemNote(osso_c)

            if newMode == 1:

                # Now in insomniac mode

                note.system_note_infoprint('Insomniac mode on!')
            else:

                # Now out of insomniac mode

                note.system_note_infoprint('Insomniac mode off...')

##### Not needed, taken care of by command line options...
# ........elif (event.key == 285):
# ............currTime = myTime.time()
# ............if (currTime - defaultDownTime > 5):
# ................#print "Default requested!"
# ................dialog = hildon.Note("confirmation", (hildon.Window(), "Really force-clear all FlipClock Alarms from system?", gtk.STOCK_DIALOG_WARNING))
# ................dialog.set_button_texts("Yes", "No")
# ................resp = dialog.run()
# ................dialog.destroy()
# ................
# ................if (resp == gtk.RESPONSE_OK):
# ....................print "Reset demanded"
# ................
# ................
# ....elif event.type == KEYDOWN:
# ........#Menu Key is pressed
# ........if (event.key == 285):
# ............defaultDownTime = myTime.time()

    if ci.inactive == 0 or ci.charging == 1:
        myTime.sleep(0.01)
    else:

        # inactive and not charging
        # sleep in a little since nobody's watching

        myTime.sleep(0.1)

    return 1


###############################################################################
# clockEventRedraw
#
# Function will be called to redraw the clock. It's initially triggered by a timeout
# and will automatically set itself up to be called again at the next minute change
# if the system is active; if the tablet is inactive then the event does not get fired
# again until the system resumes use.
###############################################################################


def drawClockEvent():

    # Draw flip as per Ciro's 0.1.3 modification

    ci_flip.flipclock()

    # Redraw the clock

    ci_clock.clock()

    # recalculate time for clock event if system is active

    if ci.inactive == 0 or ci.charging == 1:
        ctime = myTime.ctime()
        gobject.timeout_add((60 - int(str(ctime[17]) + str(ctime[18])))
                            * 1000, drawClockEvent)


############################### D-BUS Event Handling ##############################

##################################################################################
# deviceStateChange
# As per libosso device state, this is a callback that takes arguments:
# shutdown, save_unsaved_data, memory_low, system_inactivity, message, loop
# More details of their meanings here:
# http://maemo.org/api_refs/4.1/libosso-2.16-1/
#
# Anyways, in this case all we're doing is watching to see if the device is active or not, and setting
# the inactivity flag accordingly. Also, if the device does return to activity then the drawClock function is called
# to start displaying again.
#
##################################################################################


def deviceStateChangeEvent(
    shutdown,
    save_unsaved_data,
    memory_low,
    system_inactivity,
    message,
    loop,
    ):
    print 'System Inactivity: ', system_inactivity
    ci.inactive = system_inactivity

    if ci.inactive == 0 and ci.charging == 0:

        # Just returned from inactivity

        drawClockEvent()

    return False


####################################################################################
#
# checkForAlarm
# Simple pointer to call the alarm check on startup that LABAUDIO needed... since his tablet
# doesn't take dbus calls or somethign odd...
####################################################################################


def checkForAlarm():

    # damn you LABAUDIO

    ci_alarm.checkForAlarm()

    if ci_config.preferences['useAlarmD'] == 0:

        # Don't want to use alarmD, so let's just run this check every minute. This needs to be a separate timeout from the drawclock
        # since it won't be affected by power states

        ctime = myTime.ctime()
        gobject.timeout_add((60 - int(str(ctime[17]) + str(ctime[18])))
                            * 1000, checkForAlarm)


