#!/usr/bin/python
# -*- coding: utf-8 -*-
import time

import ci_init as ci
import ci_gfx

# Import the gstreamer media player module

import ci_mediaPlayer

# Import event system

import ci_eventsNew as ci_events

# Import config

import ci_config

import ci_clock

# Import date functions

from datetime import date

import os
import sys
try:
    import osso
except ImportError:
    osso = None

######################################################################
# New Alarm Module 0.1.4
#
# Built upon Ciro Ippolito's original alarm playback module, but
# updated to provide more complete functionality and integration
# with alarmD based triggers, more complex alarm actions, etc
#
# Using some of Ciro Ippolito's original code
# Module by Rob Williams (jolouis)
# 03/11/09
######################################################################

# global to indicate the current alarm settings

currentRunningAlarm = None

# global to store the closest alarm to the current time

nextClosestAlarm = None

######### General Alarm Handling Function ################
###### handleAlarm ################################
#
# This function takes an alarm object as it's single argument,
# and interprets how the alarm should be presented/executed
# based on the alertMode property.
#
# Currently the supported alert modes are:
#          1 - Light display and play sound file
#
###################################################


def handleAlarm(alarmObj):
    global currentRunningAlarm

    # find out what alarm mode we're in

    if alarmObj.has_key('alertMode') == 0:

        # failed, no alarm mode specified!

        return 0

    # alarm is now running

    ci.alarmRunning = 1

    currentRunningAlarm = alarmObj

    if alarmObj['alertMode'] == 1:

        # Mode 1 is wake up and play sound

        alarmSound = alarmObj['sound']

        print 'trying to load file' + alarmSound

        # Load the sound file

        ci_mediaPlayer.mediaController.loadFile(alarmSound)

        # ci_mediaPlayer.mediaController.loadFile("file:///usr/share/flipclock/ringer.mp3")

        ci_mediaPlayer.mediaController.setCallback(stopAlarm)

        # set loop mode (default of 1 for now)

        if alarmObj.has_key('loopSound'):
            ci_mediaPlayer.mediaController.setLoopMode(alarmObj['loopSound'
                    ])

        # Fade it in

        ci_mediaPlayer.mediaController.fadeSoundIn()

    # Jump to a clock display mode

    if ci.fcmode != ci.FCMODE_CLOCK and ci.fcmode != ci.FCMODE_NIGHT:
        ci.fcmode = ci.FCMODE_CLOCK

    # redraw

    ci_clock.clock()

    # Wake up device display

    ci.device.display_state_on()


###### stopAlarm ################################
#
# Stop the currently running alarm.
#
#
#
###################################################


def stopAlarm(buttonRef):
    global currentRunningAlarm

    print 'alarm stopped'
    print currentRunningAlarm

    if currentRunningAlarm['alertMode'] == 1:
        ci_mediaPlayer.mediaController.stop()

    ci.alarmRunning = 0
    currentRunningAlarm = None
    print 'done stopping alarm'

    # redraw the clock

    ci_clock.clock()


###### checkForAlarm ################################
#
# Manual check to see if the current time lines up with an alarm
# or not. This should never be necessary, but since LABAUDIO keeps having odd
# non-launching alarms... well, here we go
#
####################################################


def checkForAlarm():
    if ci.alarmRunning == 0:
        nowTimeRaw = time.ctime()  # .ctime instead of .locatime        Ritorna: 'DAY MON DA OR:MI:SE YEAR'
        nowTime = int(nowTimeRaw[11]) * 600 + int(nowTimeRaw[12]) * 60 \
            + int(nowTimeRaw[14]) * 10 + int(nowTimeRaw[15])

        thisDay = date.today().weekday() + 1
        if thisDay == 7:

            # sunday

            thisDay = 0

        # No alarm running, so we can proceed to check to see if one is supposed to be

        for thisAlarm in ci_config.alarms:
            if int(thisAlarm['alarm_day']) == int(thisDay):

                # Found an alarm for today, now check for the time!

                thisTime = int(thisAlarm['alarm_hhmm'][0]) * 600 \
                    + int(thisAlarm['alarm_hhmm'][1]) * 60 \
                    + int(thisAlarm['alarm_hhmm'][2]) * 10 \
                    + int(thisAlarm['alarm_hhmm'][3])
                if int(thisAlarm['ampm']) == 0:
                    if int((thisAlarm['alarm_hhmm'])[0:2]) + 12 < 23:
                        thisTime = thisTime + 12 * 60

                if thisTime == nowTime:

                    # Found the alarm to run!

                    print 'found matching alarm, running'
                    handleAlarm(thisAlarm)


###### getNextAlarm ################################
#
# Function to return the next enabled alarm; if no alarms are set it returns None
#
####################################################


def getNextAlarm():

    # Start by finding out what today is...

    thisDay = date.today().weekday() + 1
    if thisDay == 7:

        # sunday

        thisDay = 0

    nowTimeRaw = time.ctime()
    nowTime = int(nowTimeRaw[11]) * 600 + int(nowTimeRaw[12]) * 60 \
        + int(nowTimeRaw[14]) * 10 + int(nowTimeRaw[15])

    # If we get to this point, then the alarm for today is either disabled or has gone passed already, so now we need to find the next one

    closestTime = 99999999999999
    closestAlarm = None

    for thisAlarm in ci_config.alarms:
        if int(thisAlarm['enabled']) == 1:

            # Found an alarm that's active!

            thisTime = int(thisAlarm['alarm_hhmm'][0]) * 600 \
                + int(thisAlarm['alarm_hhmm'][1]) * 60 \
                + int(thisAlarm['alarm_hhmm'][2]) * 10 \
                + int(thisAlarm['alarm_hhmm'][3])
            if int(thisAlarm['ampm']) == 0:
                if int((thisAlarm['alarm_hhmm'])[0:2]) + 12 < 23:
                    thisTime = thisTime + 12 * 60

            # day offset

            dayOffset = 0
            if int(thisAlarm['alarm_day']) != thisDay:

                # day adjustment required

                if int(thisAlarm['alarm_day']) > thisDay:
                    dayOffset = int(thisAlarm['alarm_day']) - thisDay
                else:

                    dayOffset = 6 - thisDay + int(thisAlarm['alarm_day'
                            ])

                thisTime = thisTime + dayOffset * 86400

            thisAlarm['daysLeft'] = dayOffset

            timeDiff = thisTime - nowTime

            # print str(thisAlarm["alarm_day"]) + " with diff " + str(timeDiff)

            if timeDiff < closestTime and timeDiff > 0:
                closestAlarm = thisAlarm
                closestTime = timeDiff

    return closestAlarm


################# nextAlarmUpToDate ###################################
#
# Simple helper function to see if the next alarm time has passed and update it
# if it has
############################################################################


def nextAlarmUpToDate(forceUpdate=0):
    global nextClosestAlarm

    if nextClosestAlarm == None or forceUpdate == 1:

        # need to fetch it

        nextClosestAlarm = getNextAlarm()
    else:
        if nextClosestAlarm['daysLeft'] == 0:

            # also, check to see if we need to update it (i.e. the last alarm has gone past now)
            # alarm is on same day as us, so check to see if time has passed or not

            alarmTime = int(nextClosestAlarm['alarm_hhmm'][0]) * 600 \
                + int(nextClosestAlarm['alarm_hhmm'][1]) * 60 \
                + int(nextClosestAlarm['alarm_hhmm'][2]) * 10 \
                + int(nextClosestAlarm['alarm_hhmm'][3])
            if int(nextClosestAlarm['ampm']) == 0:
                if int((nextClosestAlarm['alarm_hhmm'])[0:2]) + 12 < 23:
                    alarmTime = alarmTime + 12 * 60

            nowTimeRaw = time.ctime()
            nowTime = int(nowTimeRaw[11]) * 600 + int(nowTimeRaw[12]) \
                * 60 + int(nowTimeRaw[14]) * 10 + int(nowTimeRaw[15])
            if nowTime > alarmTime:

                # need to update it

                nextClosestAlarm = getNextAlarm()


################# getNextAlarmTimeString ###################################
#
# Simple helper function to get the the time string of the next alarm
# or "" if no alarm is active and comming up
############################################################################


def getNextAlarmTimeString():
    global nextClosestAlarm

    nextAlarmUpToDate()

    timeStr = '-1'
    if nextClosestAlarm != None:
        timeStr = nextClosestAlarm['alarm_hhmm']
        hh = timeStr[0:2]
        mm = timeStr[2:4]
        if ci_config.preferences['militaryTime'] == 1:
            if nextClosestAlarm['ampm'] == 0:

                # it's PM, so we need to add 12 hours

                hh = str(int(hh) + 12)
        timeStr = hh + ':' + mm

    return timeStr


############### hasNextAlarm #############################################
#
# Simple function to return 1 or 0 indicating if there's an alarm set in the
# future or not
# Ties into common global nextClosestAlarm variable to eliminte the need
# for redundant checks...
##########################################################################


def hasNextAlarm():
    global nextClosestAlarm
    nextAlarmUpToDate()

    if nextClosestAlarm != None:
        return 1
    else:
        return 0


############### getNextAlarmDayString #############################################
#
# Simple function to return the day of the week that the next alarm is set for
#
# Ties into common global nextClosestAlarm variable to eliminte the need
# for redundant checks...
###################################################################################


def getNextAlarmDayString():
    global nextClosestAlarm
    nextAlarmUpToDate()

    dayStr = ''

    if nextClosestAlarm != None:
        dayStr = ci.daysList[nextClosestAlarm['alarm_day']]

    return dayStr


############### getCountdown #############################################
#
# Returns a string indicating how much time remains until the next alarm
#
# Ties into common global nextClosestAlarm variable to eliminte the need
# for redundant checks...
##########################################################################


def getCountdown():
    global nextClosestAlarm

    countdownStr = 'N/A'

    if nextClosestAlarm != None:
        nowTimeRaw = time.ctime()
        nowTime = int(nowTimeRaw[11]) * 600 + int(nowTimeRaw[12]) * 60 \
            + int(nowTimeRaw[14]) * 10 + int(nowTimeRaw[15])

        thisTime = int(nextClosestAlarm['alarm_hhmm'][0]) * 600 \
            + int(nextClosestAlarm['alarm_hhmm'][1]) * 60 \
            + int(nextClosestAlarm['alarm_hhmm'][2]) * 10 \
            + int(nextClosestAlarm['alarm_hhmm'][3])
        thisTime = thisTime + nextClosestAlarm['daysLeft'] * 1440
        if int(nextClosestAlarm['ampm']) == 0:
            if int((nextClosestAlarm['alarm_hhmm'])[0:2]) + 12 < 23:
                thisTime = thisTime + 12 * 60

        countdownMins = thisTime - nowTime
        print countdownMins

        if countdownMins < 0:

            # some strange error, this should never be possible...

            countdownStr = 'N/A'
        else:

            # okay, now take the minutes and determine hours/minutes string

            hours = countdownMins / 60
            mins = countdownMins % 60
            countdownStr = ''
            if hours < 10:
                countdownStr = '0'
            countdownStr = countdownStr + str(hours) + ':'
            if mins < 10:
                countdownStr = '0'
            countdownStr = countdownStr + str(mins)

    return countdownStr


#################### OLD CODE #########################################
# Everything below this point is obsolete, it's just here temporarily
# for reference!!
#######################################################################

if ci.tablet == 1:
    import hildon


def countdown():
    (x0, y0, x1, y1) = ci.sv_coords

    if ci.fcmode == 0:
        pass
    elif ci.fcmode == 1:
        ci.all_min = ci.al_edi[0] * 600 + ci.al_edi[1] * 60 \
            + ci.al_edi[2] * 10 + ci.al_edi[3]
    if ci.fcmode == 3:
        y1 = y1 - 60
    if ci.hou_min > ci.all_min:  # [DEBUG]print "la sveglia e' per domani"
        remh = (1440 - ci.hou_min + ci.all_min) / 60
        remm = 1440 - ci.hou_min + ci.all_min - remh * 60
    else:

                                                # [DEBUG]print "la sveglia e' per oggi"

        remh = (ci.all_min - ci.hou_min) / 60
        remm = ci.all_min - ci.hou_min - remh * 60
    if remh < 10:
        ci.remaing[0] = 0
        ci.remaing[1] = remh
    else:
        ci.remaing[0] = remh / 10
        ci.remaing[1] = remh % 10
    if remm < 10:
        ci.remaing[2] = 0
        ci.remaing[3] = remm
    else:
        ci.remaing[2] = remm / 10
        ci.remaing[3] = remm % 10


### Function to set the N810 LED to a specific colour


def setLED(r, g, b):
    if ci.sw_led == 1:
        setLEDMode('direct')
        value = '%X:%X:%X' % (r, g, b)
        FILE = \
            open('/sys/devices/platform/i2c_omap.2/i2c-0/0-0032/color',
                 'w')
        FILE.write(value)
        FILE.close()


### Helper function to set the LED control mode ("direct" = you can set it, "run" = it works as per OS).


def setLEDMode(mode):
    if ci.sw_led == 1:
        FILE = open('/sys/devices/platform/i2c_omap.2/i2c-0/0-0032/mode'
                    , 'w')
        FILE.write(mode)
        FILE.close()


### Crazy flashing/dancing light thing... This was 100% Ciro here... I don't like the pygame.time.delay thing, but
### we'll live with it for now...


def carnevale():
    r = 250
    g = 0
    b = 0
    for i in range(1, 50):
        ci.pygame.time.delay(5)
        b = b + 5
        setLED(r, g, b)
    for i in range(1, 50):
        ci.pygame.time.delay(5)
        r = r - 5
        g = g + 2
        b = b - 5
        setLED(r, g, b)
    for i in range(1, 50):
        ci.pygame.time.delay(5)
        r = r + 5
        g = g - 2
        setLED(r, g, b)
    for i in range(1, 50):
        ci.pygame.time.delay(5)
        r = r - 5
        setLED(r, g, b)

  # Done crazyness, now put it back to it's mood setting

    setLED(*ci.moods[ci_config.preferences['mood']]['color'])


def light_sensor():
    lux = file('/sys/devices/platform/i2c_omap.2/i2c-0/0-0029/lux', 'r')
    ci.luxlevel = int(lux.read())


# [DEBUG]light_sensor()
# [DEBUG]Wakeupitsabeautifulmorning()

