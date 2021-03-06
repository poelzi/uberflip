#!/usr/bin/python
# -*- coding: utf-8 -*-
import ci_init as ci
import sys
try:
    import osso
except ImportError:
    osso = None
import os

from datetime import date

# import gtk stuff for file chooser

import pygtk
import gtk
import gobject
import hildon

import time as myTime
import calendar

import ci_gfx
import ci_clock
import ci_alarmNew as ci_alarm

# Load the configuration/preferences module

import ci_config

# copy module, needed for element copying

import copy

# Load alarmD module

try:
    import ci_alarmD
except:
    print 'disabled alarmd support'
    ci_alarmD = None

import pygame
import pygame.event
from pygame.locals import *

##Import the label classes

import ci_labels

##Import the button classes

import ci_buttons

#####################################################################
# Modulo EVENTS 0.1.4 manage the events for differents screens
# Ciro Ippolito
# 20.00 02/21/2009
#
# Updated by Rob Williams (jolouis)
# on 02/27/09 fixed quit button to dispatch quit event to main loop
# rather than trying to handle internally.
#
# On 03/04/09 implemented ci_config for buttons and preferences.
# Cleaned up and added comments to try and help keep track of what all these things do!
#
######################################################################

pospress = 0
posrelease = 0
cl_pressdown = []
cl_release = []
al_pressdown = []
al_release = []
wi_pressdown = []
wi_release = []
(
    aposx,
    aposy,
    ax,
    ay,
    aposoff,
    aposon,
    ) = ci.al_switch_coords
(
    mposx,
    mposy,
    mx,
    my,
    mposoff,
    mposon,
    ) = ci.mt_switch_coords

########################### UPDATED BY ROB ############################
# Here's the original rect maps for the various screens.
# To make it easier to follow along with, these will be replace
# with rect-maps stored in dict entries... That way we know by name which is whic
# and can do whatever we want more easily...
# So, these become obsolete, replaced by the dicts to follow...

# ************Area for the CLOCK

cl_area = [Rect(0, 0, 800, 380), Rect(530, 390, 168, 80), Rect(700,
           390, 100, 80)]  # 0 SWING UP AND DOWN
                           # 1 Night
                           # 2 EXIT

# ************Area for ALARMSET

al_area = [  # 0 H1............................
             # 1 H2................................
             # 2 M1
             # 3 M2
             # 4 ALARM SWITCH
             # 5 MOOD
             # 6 12/24 SWITCH
             # 7 ABOUT
             # 8 EXIT
             # 9 EX HELP
             # ALARM Sched 0
             # ALARM Sched sun
             # ALARM Sched mon
             # ALARM Sched tue
             # ALARM Sched wed
             # ALARM Sched thu
             # ALARM Sched fri
             # ALARM Sched sat
    Rect(28, 88, 107, 207),
    Rect(130, 88, 107, 207),
    Rect(260, 88, 107, 207),
    Rect(365, 88, 107, 207),
    Rect(aposx, aposy, ax, ay),
    Rect(707, 385, 80, 80),
    Rect(mposx, mposy, mx, my),
    Rect(504, 280, 280, 85),
    Rect(0, 0, 800, 75),
    Rect(0, 0, 0, 0),
    Rect(310, 390, 50, 53),
    Rect(360, 390, 50, 53),
    Rect(410, 390, 50, 53),
    Rect(460, 390, 50, 53),
    Rect(510, 390, 50, 53),
    Rect(560, 390, 50, 53),
    Rect(610, 390, 50, 53),
    Rect(660, 390, 50, 53),
    ]

# ************Area for WINDOW MODE

wi_area = [Rect(0, 0, 400, 320), Rect(aposx - 80, aposy - 59, ax, ay),
           Rect(mposx - 80, mposy - 59, mx, my), Rect(500 - 80, 280
           - 60, 300, 85), Rect(707 - 80, 385 - 60, 80, 80)]  # 0 Drag up
                                                              # 1 ALARM SWITCH
                                                              # 2 12/24 SWITCH
                                                              # 3 ABOUT
                                                              # 4 MOOD

# Global variable to store mouse state (down or not)
# This is used to determine if we need to monitor the mouse move or not... used by ci_eventHandlers

mouseDown = 0

#################### Button Functions #########################################
#
# These are the functions that will be associated with buttons; notice that
# some of them are used in multiple places (i.e. gotoMainClock, etc)

##### Screen/App Control Functions #####

##Toggle window/full screen mode


def toggleWindowMode(buttonRef=None):
    if ci.fcmode == ci.FCMODE_WINDOW:
        gotoClockMode(buttonRef)
    else:
        gotoWindowMode(buttonRef)


## Switch to Window Mode


def gotoWindowMode(buttonRef):
    ci.fcmode = ci.FCMODE_WINDOW

    # Redraw the clock interface

    ci_clock.clock()

    # switch into window mode

    ci.pygame.display.toggle_fullscreen()


##Switch to Alarm Control Mode


def gotoAlarmControlMode(buttonRef):

    # #crazy "animation" test!!

    crazy = 1

    ci.fcmode = ci.FCMODE_ALARM_CONTROL
    if crazy == 0:

        # No crazy, just draw it as usual
        # Initialize the alarm mode

        initializeScreen()
    else:

        # crazzzy!
        # create a buffer to store the new screen

        newScreen = pygame.Surface((800, 480))

        # draw the new screen onto the buffer

        initializeScreen(newScreen)
        slideNewScreen('down', newScreen)


## Crazy animate screen change function
# change the clock mode, then call this function instead of init directly to redraw the screen!


def slideNewScreen(direction, newScreen):

    # grab the existing screen

    oldScreen = pygame.display.get_surface().copy()

    # now animate the oldScreen moving up and the buffer coming into replace it

    for i in range(11):
        currScreen = pygame.display.get_surface()
        currScreen.fill((0, 0, 0))
        if direction == 'down':
            currScreen.blit(oldScreen, (0, 0), (0, 48 * i, 800, 480))
            currScreen.blit(newScreen, (0, 480 - 48 * i))
        elif direction == 'up':

            # Move existing up as new one appears

            currScreen.blit(oldScreen, (0, 48 * i))
            currScreen.blit(newScreen, (0, 0), (0, 480 - 48 * i, 800,
                            480))

        pygame.display.flip()
        ci.pygame.time.wait(10)


##Toggle between Day and Night Mode


def dayNightToggle(buttonRef):

    if ci.fcmode < ci.FCMODE_NIXIE:
        ci.fcmode = ci.fcmode + 1
    else:
        ci.fcmode = ci.FCMODE_CLOCK

    print 'Agggg'
    print ci.fcmode

    # if (ci.fcmode == ci.FCMODE_CLOCK):
    # ....ci.fcmode = ci.FCMODE_NIGHT
    # elif (ci.fcmode == ci.FCMODE_NIGHT):
    # ....ci.fcmode = ci.FCMODE_CLOCK

    # redraw the clock interface

    ci_clock.clock()

    # Store this setting (our default clock mode) in the preferences

    ci_config.preferences['theme'] = ci.fcmode

    # Save the updated configuration

    ci_config.savePrefs()


##Exit FlipClock


def quitApp(buttonRef):

    # Dispatch the quit event; the main loop will get the signal and do the rest...

    ci.pygame.event.post(pygame.event.Event(pygame.QUIT))


##Switch to regular clock mode


def gotoClockMode(buttonRef):
    wasWindow = 0
    if ci.fcmode == ci.FCMODE_WINDOW:
        wasWindow = 1
    elif ci.fcmode == ci.FCMODE_ALARM_CONTROL:

        # We need to sync all the alarms with the alarmD daemon just to be safe

        updateCurrentAlarm()

    ci.fcmode = ci_config.preferences['theme']

    # Redraw the clock interface

    if wasWindow:
        ci_clock.clock()
        ci.pygame.display.toggle_fullscreen()
    else:

        # create a buffer to store the new screen

        newScreen = pygame.Surface((800, 480))

        # draw the new screen onto the buffer

        ci_clock.clock(newScreen)

        slideNewScreen('up', newScreen)


def selectAlarm(buttonRef):

    # global currentAlarmNum

    # update the current alarm settings before leaving

    updateCurrentAlarm()

    # Set the current alarm to the val of the button that was pressed

    ci.currentAlarmNum = buttonRef.currentValue

    # Re-draw the alarm mode

    initializeScreen()


##### Done Screen/App Control Functions #####

##### Toggle switch/control functions #########

##Switch to set military time on or off


def setMilitaryTime(buttonRef):

    # print "Set military time"
    # print buttonRef.currentValue

    ci_config.preferences['militaryTime'] = buttonRef.currentValue

    # Save the updated configuration

    ci_config.savePrefs()

    # Re-draw the alarm mode

    initializeScreen()


    # ci_clock.clock()

##Switch to turn the currently selected alarm on or off
#
# This technically is a bit redundant since the alarm will be
# set once the user leaves the screen or chooses to show another
# alarm, but hey, just to be safe...
#


def setAlarmOnOff(buttonRef):

    # Enable or disable the alarm

    origVal = buttonRef.currentValue

    status = updateCurrentAlarm()

    if status != 1:
        buttonRef.currentValue = origVal

        # buttonRef.drawButton()

    # Re-draw the alarm mode

    initializeScreen()


def setAMPM(buttonRef):
    ci_config.alarms[ci.currentAlarmNum]['ampm'] = \
        buttonRef.currentValue


def setLoop(buttonRef):
    ci_config.alarms[ci.currentAlarmNum]['loopSound'] = \
        buttonRef.currentValue


### Function to update the selected "mood"


def setMood(buttonRef):
    if ci_config.preferences['mood'] < 5:
        ci_config.preferences['mood'] = ci_config.preferences['mood'] \
            + 1
    else:
        ci_config.preferences['mood'] = 0

    # # Set N810 LED if present

    ci_alarm.setLED(*ci.moods[ci_config.preferences['mood']]['color'])

    # Refresh to redraw the screen

    initializeScreen()

    # # Save preferences

    ci_config.savePrefs()


#######################
# updateCurrentAlarm
#
# Method to save the settings for the currently selected alarm
# to the local ci_config.alarms structure.
# This struct is then sync'd with the alarmD and config files
# later when the screen is changed
########################


def updateCurrentAlarm(showBusy=1, forceUpdate=0):

    # Enable or disable the alarm

    # did we succeed?

    success = 0

    # Store the user's prefs in the global alarms array....
    # Get the current time for the alarm from the buttons

    hour1 = screens[ci.FCMODE_ALARM_CONTROL]['buttons']['hours'
            ].firstDigit.currentValue
    hour2 = screens[ci.FCMODE_ALARM_CONTROL]['buttons']['hours'
            ].secondDigit.currentValue

    min1 = screens[ci.FCMODE_ALARM_CONTROL]['buttons']['minute1'
            ].currentValue
    min2 = screens[ci.FCMODE_ALARM_CONTROL]['buttons']['minute2'
            ].currentValue

    # Here's the tricky bit... get the timestamp that represents the next time this day of the week will come up, and this time
    # on that day...

    # start by getting the current timestamp

    now = myTime.time()

    # $today = mktime(0,0,0,date("n", $today), date("j", $today), date("Y", $today));
    # dayOnly = myTime.mktime((time.strftime("%Y", now), time

    # or we could just not care, since we're repeating...
    # let's get the time, for say,
    # 1236488400 is Sunday, March 8, 2009 @00:00:00, so let's try that as a base
    # whoops, sorry should be 1236470400 (Sunday, March 8, 2009 @00:00:00 UTC) + time.timezone (timezone offset of UTC in seconds)

    # so first, which day of the week are we? Sunday, + current alarm (0-7) times seconds in a day (86400)

    targetTime = 1236470400 + myTime.timezone + ci.currentAlarmNum \
        * 86400

    # OKAY WRONG AGAIN! You have to calculate the actual time of the event (i.e. what day it's actually scheduled for) so that
    # the dst can be accurately determined!
    # so, try once more...

    todayTest = myTime.gmtime(myTime.time())

    # find out what day of the week it is (where 0 is Monday, Sunday is 6)

    todayDay = todayTest.tm_wday

    # modify the struct to point to 00:00:00 today

    todayTest = (
        todayTest.tm_year,
        todayTest.tm_mon,
        todayTest.tm_mday,
        0,
        0,
        0,
        todayTest.tm_wday,
        todayTest.tm_yday,
        todayTest.tm_isdst,
        )

    # generate the time at the beginnig of today

    startToday = calendar.timegm(todayTest)
    if todayDay == 6:

        # If it's sunday, then our reference time is

        dayOffset = 0
    else:

        # otherwise, day offset is whatever day it is

        dayOffset = todayDay + 1

    targetDay = ci.currentAlarmNum - dayOffset
    if targetDay < 0:

        # target day is behind us in the week, so we need to jump to next week instead

        targetTime = startToday + (7 - dayOffset + ci.currentAlarmNum) \
            * 86400
    else:

        # target day is ahead of or current day, so we're good

        targetTime = startToday + targetDay * 86400

    targetTime = targetTime + myTime.timezone

    # now, we add the current time specified
    # Minutes are always the same, just multiply by 60 seconds

    extra = (min1 * 10 + min2) * 60

    # Get the hours as an int

    hoursTotal = hour1 * 10 + hour2

    # isAMPM.. AM == 1, PM == 0

    isAMPM = 1

    # now add the hours, which are either am/pm, or 24 hour... let's pretend for the moment there always 24
    # don't forget, 3600 seconds in an hour...

    if ci_config.preferences['militaryTime']:
        extra = extra + hoursTotal * 3600

        # Convert to 12 hour time to store in array

        if hoursTotal == 0:
            hoursStr = '12'
            isAMPM = 1
        elif 0 < hoursTotal < 10:
            hoursStr = '0' + str(hoursTotal)
            isAMPM = 1
        elif 9 < hoursTotal < 13:
            hoursStr = str(hoursTotal)
            isAMPM = 1
        else:
            hoursStr = str(hoursTotal)
            isAMPM = 0
    else:

        # Get the AM/PM setting... AM == 1, PM ==0

        ampm = screens[ci.FCMODE_ALARM_CONTROL]['buttons']['ampmSwitch'
                ].currentValue
        isAMPM = ampm
        if hoursTotal == 12 and ampm == 1:

            # 12 am = 00

            hoursTotal = 0
        elif hoursTotal == 12 and ampm == 0:

            # 12pm = 12.. gotta do something, so...

            hoursTotal = hoursTotal
        elif ampm == 0:

            # pm value

            hoursTotal = 12 + hoursTotal
        extra = extra + hoursTotal * 3600

        # string to store the hours (Always stored in 12 hour format)

        hoursStr = str(hour1) + str(hour2)

    # so finally, our target time is

    targetTime = targetTime + extra

    # check for DST

    if myTime.localtime(targetTime).tm_isdst == 1:

        # DST is active, so adjust time accordingly

        adjustment = myTime.timezone - myTime.altzone

        # If DST, subtract the difference of the zones..

        targetTime = targetTime - adjustment

    # original alarm time

    originalAlarmTime = \
        ci_config.alarms[ci.currentAlarmNum]['alarm_time']

    # set the alarm propeties

    ci_config.alarms[ci.currentAlarmNum]['alarm_time'] = targetTime
    ci_config.alarms[ci.currentAlarmNum]['alarm_hhmm'] = hoursStr \
        + str(min1) + str(min2)
    ci_config.alarms[ci.currentAlarmNum]['ampm'] = isAMPM

    # what action needs to be taken?

    action = ''

    # #Check if update was forced

    if forceUpdate:
        if screens[ci.FCMODE_ALARM_CONTROL]['buttons']['alarmSwitch'
                ].currentValue == 1:
            action = 'enable'
        elif screens[ci.FCMODE_ALARM_CONTROL]['buttons']['alarmSwitch'
                ].currentValue == 0:
            action = 'disable'

    if originalAlarmTime != targetTime \
        and screens[ci.FCMODE_ALARM_CONTROL]['buttons']['alarmSwitch'
            ].currentValue == 1:

        # Alarm should be on, but time has changed so update it!
        # print "updating alarm"

        runScreenState('setBusy')
        action = 'enable'
    elif screens[ci.FCMODE_ALARM_CONTROL]['buttons']['alarmSwitch'
            ].currentValue == 1 \
        and ci_config.alarms[ci.currentAlarmNum]['enabled'] != 1:

        # success = ci_alarmD.enableAlarm(ci.currentAlarmNum)

        # Alarm has been set to enabled, so apply the current settings

        runScreenState('setBusy')

        # print "setting alarm req"
        # enable alarm
        # success = ci_alarmD.enableAlarm(ci.currentAlarmNum)

        action = 'enable'
    elif screens[ci.FCMODE_ALARM_CONTROL]['buttons']['alarmSwitch'
            ].currentValue == 0 \
        and ci_config.alarms[ci.currentAlarmNum]['enabled'] != 0:

        # disable alarm
        # print "unsetting alarm req"
        # runScreenState("setBusy")
        # success = ci_alarmD.disableAlarm(ci.currentAlarmNum)

        action = 'disable'

    if action == 'enable':
        if showBusy:

            # show the busy screen

            runScreenState('setBusy')

        # Now do the update

        success = ci_alarmD.enableAlarm(ci.currentAlarmNum)
    elif action == 'disable':

        if showBusy:

            # show the busy screen

            runScreenState('setBusy')

        # Now do the update

        success = ci_alarmD.disableAlarm(ci.currentAlarmNum)
    else:

        # No action is required, so assume we succeeded

        success = 1

    if success != 1:

        # Failed for some reason

        osso_c = osso.Context('osso_test_note', '0.0.1', False)
        note = osso.SystemNote(osso_c)
        result = \
            note.system_note_dialog('Failed while attempting to set alarm'
                                    , type='notice')

        screens[ci.FCMODE_ALARM_CONTROL]['buttons']['alarmSwitch'
                ].currentValue = success
        screens[ci.FCMODE_ALARM_CONTROL]['buttons']['alarmSwitch'
                ].drawButton()

    # handled by enable/disable alarm calls
    # update the config file since alarm state has changed

    ci_config.savePrefs()
    print 'Done alarm update'
    if showBusy:
        runScreenState('clearBusy')

    return success


##### Done Toggle switch/control functions ####

##### General Alarm Functions #################

#####chooseAlarmFile ##########################
#
# Function to select an MP3 file to use as the alarm sound
###############################################


def chooseAlarmSound(buttonRef):

    if ci.modalOpen == 0:
        ci.modalOpen = 1
        runScreenState('setBusy')

        dialog = hildon.FileChooserDialog(hildon.Window(),
                gtk.FILE_CHOOSER_ACTION_OPEN)
        response = dialog.run()
        dialog.hide()

        ci.modalOpen = 0

        fileName = dialog.get_filename()

        if response == gtk.RESPONSE_OK:
            print 'Selected file'
            if fileName.lower().endswith('mp3'):

                # good to go

                ci_config.alarms[ci.currentAlarmNum]['sound'] = \
                    'file://' + fileName
            else:

                # Redraw the file display in a moment...
                # initializeScreen()

                osso_c = osso.Context('osso_test_note', '0.0.1', False)
                note = osso.SystemNote(osso_c)
                result = \
                    note.system_note_dialog('Sorry, only .mp3 files are working right now'
                        , type='notice')

        # Save the alarm (to prevent the redraw from toasting values

        updateCurrentAlarm(0, 1)

        runScreenState('clearBusy')


######## doSnooze #####################
#
# function to snooze the current alarm
#######################################


def doSnooze(buttonRef):

    # first, get a copy of the currently running alarm

    snoozeAlarm = copy.deepcopy(ci_alarm.currentRunningAlarm)

    # finally, stop the current alarm since its been snoozed

    ci_alarm.stopAlarm(buttonRef)

    # Display the "Yo it's snoozing" thing

    snoozeWarning = ci_labels.textLabel(Rect(100, 300, 650, 75),
            'Snoozing for ' + str(snoozeAlarm['snoozeTime']) + '...')
    snoozeWarning.setColour((230, 230, 230))
    snoozeWarning.drawLabel()

    # ## To prevent snoozes from getting lost and continuously happening, let's make 'em internal instead...
    # update it with the appropriate alarmD stuff

    if ci_config.preferences['alarmDSnooze'] == 1:
        time = myTime.time()
        newTime = int(time) + int(snoozeAlarm['snoozeTime']) * 60

        # newTime = int(time) + 120

        # set the snooze time

        snoozeAlarm['alarm_time'] = newTime

        # set the snooze title

        snoozeAlarm['title'] = 'Snoozed Alarm'

        # set the recurrence to one since this is a snooze

        snoozeAlarm['recurrence_count'] = 0

        snoozeAlarm['recurrence'] = 0

        # now set the alarm

        ci_alarmD.setFlipAlarm(snoozeAlarm)
    else:

        # Internal, no alarmD for snoozing!
        # This is actually pretty easy to do...

        newTime = int(snoozeAlarm['snoozeTime']) * 60 * 1000

        # newTime = 120 *1000

        print 'no alarmD snooze!'

        # set the snooze time

        snoozeAlarm['alarm_time'] = myTime.time() + newTime

        # set the snooze title

        snoozeAlarm['title'] = 'Snoozed Alarm'

        # set the recurrence to one since this is a snooze

        snoozeAlarm['recurrence_count'] = 0

        snoozeAlarm['recurrence'] = 0
        gobject.timeout_add(newTime, ci_alarm.handleAlarm, snoozeAlarm)

    print 'snoozed'

    # should really call ci.clock() but then, ci.clock() should be redundant, and be called by initializeScreen instead....
    # however, in any event this screws things up, so stay away for now...

    gobject.timeout_add(5000, ci_clock.clock)


#################### Done Button Functions #########################################

################### Dict Screen Definitions ######################################
############ Clock Screen ##############

###### Buttons ########

clockScreenButtons = {}

##Swing up/down to change screens

clockScreenButtons['swinger'] = ci_buttons.dragButton(Rect(0, 0, 800,
        380))
clockScreenButtons['swinger'].addDragCallback('up', 20, gotoWindowMode)
clockScreenButtons['swinger'].addDragCallback('down', 20,
        gotoAlarmControlMode)

# disable dragging if alarm running

clockScreenButtons['swinger'].setEnableCondition('ci.alarmRunning', 0)

##Day/Night toggle button

clockScreenButtons['nightDay'] = ci_buttons.clickButton(Rect(530, 390,
        168, 80), dayNightToggle)

## Disable night/day when alarm is running so you don't change modes by accident when hitting snooze

clockScreenButtons['nightDay'].setEnableCondition('ci.alarmRunning', 0)

##Exit button

clockScreenButtons['exit'] = ci_buttons.clickButton(Rect(700, 390, 100,
        80), quitApp)

## Disable exit if alarm running so you don't quite by accident when hitting snooze

clockScreenButtons['exit'].setEnableCondition('ci.alarmRunning', 0)

######## Alarm mode buttons #############
# these buttons are only active when the alarm is playing
#########################################

clockScreenButtons['alarmOff'] = ci_buttons.clickButton(Rect(0, 0, 800,
        380), ci_alarm.stopAlarm)
clockScreenButtons['alarmOff'].setEnableCondition('ci.alarmRunning', 1)

clockScreenButtons['snooze'] = ci_buttons.clickButton(Rect(0, 380, 800,
        100), doSnooze)
clockScreenButtons['snooze'].setEnableCondition('ci.alarmRunning', 1)

###### Done Buttons #######

###### Labels #############

clockScreenLabels = {}

# Alarm Time Label (alarm off)
# clockScreenLabels["alarmTime"] = ci_labels.textLabel(Rect(87, 400, 114, 55), "", "ci_alarm.getNextAlarmTimeString()")
# clockScreenLabels["alarmTime"].setColour((110, 110, 110))
# clockScreenLabels["alarmTime"].setEnableCondition("ci_alarm.hasNextAlarm()", 1)

##Alarm time label (alarmOn)

clockScreenLabels['alarmTimeOn'] = ci_labels.textLabel(Rect(87, 400,
        114, 55), '', 'ci_alarm.getNextAlarmTimeString()')
clockScreenLabels['alarmTimeOn'].setColour((ci.mr, ci.mg, ci.mb))
clockScreenLabels['alarmTimeOn'
                  ].setEnableCondition('ci_alarm.hasNextAlarm()', 1)

##Alarm on helpers

clockScreenLabels['alarmEngaged'] = ci_labels.textLabel(Rect(114, 389,
        114, 55), '', 'ci_alarm.getNextAlarmDayString()')
clockScreenLabels['alarmEngaged'].setColour((ci.mr, ci.mg, ci.mb))
clockScreenLabels['alarmEngaged'].setFont(ci.flipFonts['small'])
clockScreenLabels['alarmEngaged'
                  ].setEnableCondition('ci_alarm.hasNextAlarm()', 1)

clockScreenLabels['alarmEngaged2'] = ci_labels.textLabel(Rect(104, 443,
        114, 55), 'ENGAGED')
clockScreenLabels['alarmEngaged2'].setColour((ci.mr, ci.mg, ci.mb))
clockScreenLabels['alarmEngaged2'].setFont(ci.flipFonts['small'])
clockScreenLabels['alarmEngaged2'
                  ].setEnableCondition('ci_alarm.hasNextAlarm()', 1)

##Alarm countdown

clockScreenLabels['alarmCountdown'] = ci_labels.textLabel(Rect(233,
        402, 55, 114), '', 'ci_alarm.getCountdown()')
clockScreenLabels['alarmCountdown'].setAngle(90)
clockScreenLabels['alarmCountdown'].setFont(ci.flipFonts['small'])
clockScreenLabels['alarmCountdown'].setColour((ci.mr, ci.mg, ci.mb))
clockScreenLabels['alarmCountdown'
                  ].setEnableCondition('ci_alarm.hasNextAlarm()', 1)

##Date Labels

clockScreenLabels['dateLabel1'] = ci_labels.textLabel(Rect(293, 395,
        114, 55), '', 'ci.time.strftime("%b - %Y")')
clockScreenLabels['dateLabel1'].setColour((ci.mr, ci.mg, ci.mb))
clockScreenLabels['dateLabel1'].setFont(ci.flipFonts['small'])
clockScreenLabels['dateLabel1'].setEnableCondition('ci.alarmRunning', 0)

clockScreenLabels['dateLabel2'] = ci_labels.textLabel(Rect(291, 417,
        220, 80), '', 'ci.time.strftime("%a %d")')
clockScreenLabels['dateLabel2'].setColour((ci.mr, ci.mg, ci.mb))
clockScreenLabels['dateLabel2'].setEnableCondition('ci.alarmRunning', 0)

#### "Mood" Labels #####
## Top

clockScreenLabels['moodTop'] = ci_labels.imageLabel(Rect(0, 20, 800,
        40), {}, 1)
clockScreenLabels['moodTop'
                  ].setDefaultCondition('ci_config.preferences["mood"]')

## Bottom

clockScreenLabels['moodBottom'] = ci_labels.imageLabel(Rect(0, 380,
        800, 40), {}, 1)
clockScreenLabels['moodBottom'
                  ].setDefaultCondition('ci_config.preferences["mood"]')

# Add the images

i = 0
for thisImg in ci.moods:
    clockScreenLabels['moodTop'].addImage(i, thisImg['image'])
    clockScreenLabels['moodBottom'].addImage(i, thisImg['image'])
    i = i + 1

#### Alarm is playing labels ##########

## Snooze background

clockScreenLabels['snoozeBG'] = ci_labels.imageLabel(Rect(0, 383, 800,
        90), {1: ci.buttonImages['snoozeBG']}, 2)
clockScreenLabels['snoozeBG'].setDefaultCondition('ci.alarmRunning')

## Snooze text

clockScreenLabels['snoozeText1'] = ci_labels.textLabel(Rect(100, 400,
        400, 60), 'Snooze for another', '', 3)
clockScreenLabels['snoozeText1'].setEnableCondition('ci.alarmRunning',
        1)

## Snooze time

clockScreenLabels['snoozeText2'] = ci_labels.textLabel(Rect(500, 400,
        150, 60), '', 'ci_alarm.currentRunningAlarm["snoozeTime"]', 3)
clockScreenLabels['snoozeText2'].setEnableCondition('ci.alarmRunning',
        1)

###### Done Labels ########

############ Done Clock Screen #################

############ Clock Night Screen ##############

###### Buttons ########

##Buttons are re-used from the regular clock day-screen, just the labels need to change

###### Done Buttons #######

###### Labels #############

clockNightScreenLabels = {}

# Alarm Time Label (alarm off)
# clockNightScreenLabels["alarmTime"] = ci_labels.textLabel(Rect(87, 400, 114, 55), "", "ci_alarm.getNextAlarmTimeString()")
# clockNightScreenLabels["alarmTime"].setColour((110, 110, 110))
# clockNightScreenLabels["alarmTime"].setEnableCondition("ci_alarm.hasNextAlarm()", 1)

##Alarm time label (alarmOn)

clockNightScreenLabels['alarmTimeOn'] = ci_labels.textLabel(Rect(87,
        400, 114, 55), '', 'ci_alarm.getNextAlarmTimeString()')
clockNightScreenLabels['alarmTimeOn'].setColour((ci.mr, ci.mg, ci.mb))
clockNightScreenLabels['alarmTimeOn'
                       ].setEnableCondition('ci_alarm.hasNextAlarm()',
        1)

##Alarm on helpers

clockNightScreenLabels['alarmEngaged'] = ci_labels.textLabel(Rect(114,
        389, 114, 55), '', 'ci_alarm.getNextAlarmDayString()')
clockNightScreenLabels['alarmEngaged'].setColour((ci.mr, ci.mg, ci.mb))
clockNightScreenLabels['alarmEngaged'].setFont(ci.flipFonts['small'])
clockNightScreenLabels['alarmEngaged'
                       ].setEnableCondition('ci_alarm.hasNextAlarm()',
        1)

clockNightScreenLabels['alarmEngaged2'] = ci_labels.textLabel(Rect(104,
        443, 114, 55), 'ENGAGED')
clockNightScreenLabels['alarmEngaged2'].setColour((ci.mr, ci.mg, ci.mb))
clockNightScreenLabels['alarmEngaged2'].setFont(ci.flipFonts['small'])
clockNightScreenLabels['alarmEngaged2'
                       ].setEnableCondition('ci_alarm.hasNextAlarm()',
        1)

##Alarm countdown

clockNightScreenLabels['alarmCountdown'] = \
    ci_labels.textLabel(Rect(233, 402, 55, 114), '',
                        'ci_alarm.getCountdown()')
clockNightScreenLabels['alarmCountdown'].setAngle(90)
clockNightScreenLabels['alarmCountdown'].setFont(ci.flipFonts['small'])
clockNightScreenLabels['alarmCountdown'].setColour((ci.mr, ci.mg,
        ci.mb))
clockNightScreenLabels['alarmCountdown'
                       ].setEnableCondition('ci_alarm.hasNextAlarm()',
        1)

##Date Labels

clockNightScreenLabels['dateLabel1'] = ci_labels.textLabel(Rect(293,
        395, 114, 55), '', 'ci.time.strftime("%b - %Y")')
clockNightScreenLabels['dateLabel1'].setColour((ci.mr, ci.mg, ci.mb))
clockNightScreenLabels['dateLabel1'].setFont(ci.flipFonts['small'])
clockNightScreenLabels['dateLabel1'
                       ].setEnableCondition('ci.alarmRunning', 0)

clockNightScreenLabels['dateLabel2'] = ci_labels.textLabel(Rect(291,
        417, 220, 80), '', 'ci.time.strftime("%a %d")')
clockNightScreenLabels['dateLabel2'].setColour((ci.mr, ci.mg, ci.mb))
clockNightScreenLabels['dateLabel2'
                       ].setEnableCondition('ci.alarmRunning', 0)

#### Alarm is playing labels ##########

## Snooze background

clockNightScreenLabels['snoozeBG'] = ci_labels.imageLabel(Rect(0, 383,
        800, 90), {1: ci.buttonImages['snoozeBG']}, 1)
clockNightScreenLabels['snoozeBG'].setDefaultCondition('ci.alarmRunning'
        )

## Snooze text

clockNightScreenLabels['snoozeText1'] = ci_labels.textLabel(Rect(100,
        400, 400, 60), 'Snooze for another', '', 2)
clockNightScreenLabels['snoozeText1'
                       ].setEnableCondition('ci.alarmRunning', 1)

## Snooze time

clockNightScreenLabels['snoozeText2'] = ci_labels.textLabel(Rect(500,
        400, 150, 60), '', 'ci_alarm.currentRunningAlarm["snoozeTime"]'
        , 2)
clockNightScreenLabels['snoozeText2'
                       ].setEnableCondition('ci.alarmRunning', 1)

###### Done Labels ########

############ Done Clock Night Screen #################

############ Alarm Settings Screen ######

###### Buttons ########

alarmControlScreenButtons = {}

##H1 & 2 Combined

alarmControlScreenButtons['hours'] = \
    ci_buttons.doubleHoursScroller(Rect(28, 88, 107, 207), Rect(130,
                                   88, 107, 207),
                                   'ci_config.preferences["militaryTime"]'
                                   )
alarmControlScreenButtons['hours'
                          ].setInitValues('ci_config.alarms[ci.currentAlarmNum]["alarm_hhmm"][0]'
        , 'ci_config.alarms[ci.currentAlarmNum]["alarm_hhmm"][1]')

##M1 Scroller

alarmControlScreenButtons['minute1'] = \
    ci_buttons.digitScroller(Rect(257, 88, 107, 207), None, 0, [0, 5])

# set the default value

alarmControlScreenButtons['minute1'
                          ].setInitValue('ci_config.alarms[ci.currentAlarmNum]["alarm_hhmm"][2]'
        )

##M2 Scroller

alarmControlScreenButtons['minute2'] = \
    ci_buttons.digitScroller(Rect(358, 88, 107, 207), None, 0)

# set the default value

alarmControlScreenButtons['minute2'
                          ].setInitValue('ci_config.alarms[ci.currentAlarmNum]["alarm_hhmm"][3]'
        )

##Alarm on/off switch

alarmControlScreenButtons['alarmSwitch'] = \
    ci_buttons.slideButton(Rect(*ci.al_switch_coords[0:4]),
                           setAlarmOnOff,
                           'ci_config.alarms[ci.currentAlarmNum]["enabled"]'
                           , ci.switch_images['onoff'],
                           ci.switch_masks['alDark'])

##Alarm am/pm switch

alarmControlScreenButtons['ampmSwitch'] = \
    ci_buttons.slideButton(Rect(664, 194, 102, 70), setAMPM,
                           'ci_config.alarms[ci.currentAlarmNum]["ampm"]'
                           , ci.switch_images['ampm'],
                           ci.switch_masks['alDark'])

# set switch enable condition so that it's only enabled if 24 hour mode == 0

alarmControlScreenButtons['ampmSwitch'
                          ].setEnableCondition('ci_config.preferences["militaryTime"]'
        , 0)

##Alarm MP3 File chooser button

alarmControlScreenButtons['fileChooser'] = \
    ci_buttons.clickButton(Rect(504, 283, 150, 82), chooseAlarmSound)

##Alarm MP3 Loop/Once switch

alarmControlScreenButtons['loopSwitch'] = \
    ci_buttons.slideButton(Rect(664, 290, 102, 70), setLoop,
                           'ci_config.alarms[ci.currentAlarmNum]["loopSound"]'
                           , ci.switch_images['loop'],
                           ci.switch_masks['alMed'])

alarmControlScreenButtons['mood'] = ci_buttons.clickButton(Rect(707,
        385, 80, 80), setMood)  # Mood selector thing

##Switch for military time

alarmControlScreenButtons['mtSwitch'] = \
    ci_buttons.slideButton(Rect(580, 400, 102, 70), setMilitaryTime,
                           'ci_config.preferences["militaryTime"]',
                           ci.switch_images['1224'],
                           ci.switch_masks['alLight'])

##About button needs to be relocated, deal with that later...
##alarmControlScreenButtons["about"] = Rect (504,280,280, 85)    #About Button

##Close the alarm settings window and go back to the clock

alarmControlScreenButtons['backToClock'] = \
    ci_buttons.dragButton(Rect(0, 0, 800, 75))
alarmControlScreenButtons['backToClock'].addDragCallback('up', 20,
        gotoClockMode)

# alarmControlScreenButtons["exitHelp"] = Rect (0,0,0, 0)        #Exit Help screen

for i in range(7):
    alarmControlScreenButtons['alarmSched' + str(i)] = \
        ci_buttons.clickButton(Rect(40 + i * 50, 390, 50, 53),
                               selectAlarm, i)  # Alarm Day X button

###### Done Buttons #######

###### Labels #############

alarmControlScreenLabels = {}

# AM/PM Switch label

alarmControlScreenLabels['ampmSwitch'] = ci_labels.textLabel(Rect(520,
        190, 150, 70), 'AM/PM')
alarmControlScreenLabels['ampmSwitch'
                         ].setEnableCondition('ci_config.preferences["militaryTime"]'
        , 0)

##Alarm MP3 File chooser label

alarmControlScreenLabels['fileChooser'] = ci_labels.textLabel(Rect(512,
        282, 150, 67), 'Sound')
alarmControlScreenLabels['fileLabel'] = ci_labels.textLabel(Rect(512,
        328, 150, 67), '',
        'os.path.basename(ci_config.alarms[ci.currentAlarmNum]["sound"])'
        )
alarmControlScreenLabels['fileLabel'].setFont(ci.flipFonts['small'])

# Alarm Day of the Week Label

alarmControlScreenLabels['dayLabel'] = ci_labels.textLabel(Rect(222,
        330, 90, 30), '',
        'ci.daysList[ci_config.alarms[ci.currentAlarmNum]["alarm_day"]]'
        )
alarmControlScreenLabels['dayLabel'].setFont(ci.flipFonts['small'])

# alarm Day X Indicators

for i in range(7):
    alarmControlScreenLabels['alarmSched' + str(i)] = \
        ci_labels.imageLabel(Rect(46 + i * 50, 390, 50, 61),
                             {0: ci.alarmIcons['off'],
                             1: ci.alarmIcons['on']})  # Alarm Day X button
    alarmControlScreenLabels['alarmSched'
                             + str(i)].setDefaultCondition('ci_config.alarms['
             + str(i) + ']["enabled"]')

    # #And image to cover/overlay to show which alarm is selected

    alarmControlScreenLabels['alarmSel' + str(i)] = \
        ci_labels.imageLabel(Rect(39 + i * 50, 387, 48, 65),
                             {0: ci.alarmIcons['nonSelected'],
                             1: ci.alarmIcons['selected']}, 1)  # Alarm Selection Indicator
    alarmControlScreenLabels['alarmSel'
                             + str(i)].setDefaultCondition('int('
            + str(i) + ') == ci.currentAlarmNum')

#### "Mood" Labels #####
## Top

alarmControlScreenLabels['moodTop'] = ci_labels.imageLabel(Rect(0, 20,
        800, 40), {}, 1)
alarmControlScreenLabels['moodTop'
                         ].setDefaultCondition('ci_config.preferences["mood"]'
        )

## Bottom

alarmControlScreenLabels['moodBottom'] = ci_labels.imageLabel(Rect(0,
        70, 800, 40), {}, 1)
alarmControlScreenLabels['moodBottom'
                         ].setDefaultCondition('ci_config.preferences["mood"]'
        )

# Add the images

i = 0
for thisImg in ci.moods:
    alarmControlScreenLabels['moodTop'].addImage(i, thisImg['image'])
    alarmControlScreenLabels['moodBottom'].addImage(i, thisImg['image'])
    i = i + 1

###### Done Labels ########

############ Done Alarm Screen #################

############ Window Mode Screen #################

###### Buttons ########

windowModeScreenButtons = {}

# Click to return to clock mode...

windowModeScreenButtons['backToClock'] = ci_buttons.clickButton(Rect(0,
        0, 400, 320), gotoClockMode)

# Alarm switch co-ordinates, as specified in ci_init
# windowModeScreenButtons["alarmSwitch"] = ci_buttons.slideButton(Rect(*ci.al_switch_coords[1:5]), setMilitaryTime, ci_config.preferences["militaryTime"], ci.switch_images["1224"], ci.switch_masks["alDark"])

# Switch for military time

windowModeScreenButtons['mtSwitch'] = \
    ci_buttons.slideButton(Rect(ci.mt_switch_coords[0] - 80,
                           ci.mt_switch_coords[1] - 59,
                           ci.mt_switch_coords[2],
                           ci.mt_switch_coords[3]), setMilitaryTime,
                           'ci_config.preferences["militaryTime"]',
                           ci.onoff_switch[2], ci.onoff_switch[0])

# windowModeScreenButtons["about"] = Rect (500-80,280-60,300, 85)       #About Button

# windowModeScreenButtons["mood"] = Rect (707-80,385-60,80, 80)         #Mood selector thing

###### Done Buttons #######

###### Labels #############

###### Done Labels ########

############ Done Window Mode Screen #################

########### Generic Labels ###########################
# (apply to all or multiple screens )
######################################################

# labels for when the clock is busy

busyLabels = {}
busyLabels['waitScreen'] = ci_labels.imageLabel(Rect(0, 0, 800, 480),
        {1: ci.buttonImages['waitScreen']}, 1)
busyLabels['waitScreen'].setDefaultCondition('ci.clockBusy')

########### Done Generic Labels ######################

############ Overall screen container element ###########

screens = {}
screens[ci.FCMODE_CLOCK] = {}
screens[ci.FCMODE_CLOCK]['title'] = 'Main Clock Screen'
screens[ci.FCMODE_CLOCK]['background'] = ci.cl_bground
screens[ci.FCMODE_CLOCK]['buttons'] = clockScreenButtons
screens[ci.FCMODE_CLOCK]['labels'] = clockScreenLabels

screens[ci.FCMODE_NIGHT] = {}
screens[ci.FCMODE_NIGHT]['title'] = 'Night Clock Screen'
screens[ci.FCMODE_NIGHT]['backgroundColourRef'] = \
    'ci.moods[ci_config.preferences["mood"]]["nightColor"]'
screens[ci.FCMODE_NIGHT]['background'] = ci.ni_bground
screens[ci.FCMODE_NIGHT]['buttons'] = clockScreenButtons
screens[ci.FCMODE_NIGHT]['labels'] = clockNightScreenLabels

# screens[ci.FCMODE_NIXIE] = {}
# screens[ci.FCMODE_NIXIE]["title"] = "Nixie Clock Screen"
# screens[ci.FCMODE_NIXIE]["background"] = ci.nx_bground
# screens[ci.FCMODE_NIXIE]["buttons"] = clockScreenButtons
# screens[ci.FCMODE_NIXIE]["labels"] = clockScreenLabels

screens[ci.FCMODE_ALARM_CONTROL] = {}
screens[ci.FCMODE_ALARM_CONTROL]['title'] = 'Alarm Control Screen'
screens[ci.FCMODE_ALARM_CONTROL]['background'] = ci.al_bground
screens[ci.FCMODE_ALARM_CONTROL]['buttons'] = alarmControlScreenButtons
screens[ci.FCMODE_ALARM_CONTROL]['labels'] = alarmControlScreenLabels
screens[ci.FCMODE_ALARM_CONTROL]['stateLabels'] = busyLabels

screens[ci.FCMODE_WINDOW] = {}
screens[ci.FCMODE_WINDOW]['title'] = 'Window Mode Screen'
screens[ci.FCMODE_WINDOW]['buttons'] = windowModeScreenButtons

############# DONE dict Screen Definitions ########################################

######################## Event Driver/Handlers ####################################
#
# This is the last part of the equation, that ties all of the buttons defined for
# which ever screen is active to the actual event callbacks.
# (i.e. from ci_eventHandlers, the tap_down, tap_release, or tap_drag functions
# are called, which then check to see which screen we're on,and pass the event
# along to each button that's setup there)
#

############## initializeScreen #########################
#
# This method handles the initial setup of the given screen and buttons/etc
#
#########################################################


def initializeScreen(screenBuf=None):

    # is there a screen definition for the current screen

    if screens.has_key(ci.fcmode):

        # setup the temp buffer to draw on

        if screenBuf == None:
            myScreen = pygame.display.get_surface()
        else:
            myScreen = screenBuf

        # Draw background colour if set

        if screens[ci.fcmode].has_key('backgroundColourRef'):
            myScreen.fill(eval(screens[ci.fcmode]['backgroundColourRef'
                          ]))

        # Draw background

        if screens[ci.fcmode].has_key('background'):

            myScreen.blit(screens[ci.fcmode]['background'], (0, 0))

        # okay, check to see if buttons are defined

        if screens[ci.fcmode].has_key('buttons'):

            # okay buttons are defined, so loop over them and initialize them

            for (buttonName, buttonVal) in screens[ci.fcmode]['buttons'
                    ].items():

                # setup default

                try:
                    if hasattr(buttonVal, 'setDefault'):
                        buttonVal.setDefault()
                except:
                    print sys.exc_info()[0]
                    print sys.exc_info()[1]
                    print sys.exc_info()[2]

                # Set the initial value

                try:
                    if hasattr(buttonVal, 'handleInit'):
                        buttonVal.handleInit(myScreen)
                except:
                    print sys.exc_info()[0]
                    print sys.exc_info()[1]
                    print sys.exc_info()[2]

                # render the button

                try:
                    if hasattr(buttonVal, 'drawButton'):
                        buttonVal.drawButton(myScreen)
                except:
                    print sys.exc_info()[0]
                    print sys.exc_info()[1]
                    print sys.exc_info()[2]

        # next, check to see if labels are defined

        if screens[ci.fcmode].has_key('labels'):

            # okay labels are defined, so loop over them and initialize them

            theseLabels = copy.copy(screens[ci.fcmode]['labels'])

            i = 0
            while len(theseLabels) > 0:
                for (labelName, nullVal) in theseLabels.items():
                    labelVal = screens[ci.fcmode]['labels'][labelName]

                    # Render based on z-Index

                    if labelVal.zIndex == i:

                        # setup default

                        try:
                            if hasattr(labelVal, 'setDefault'):
                                labelVal.setDefault()
                        except:
                            pass
                        try:
                            if hasattr(labelVal, 'drawLabel'):
                                labelVal.drawLabel(myScreen)
                        except:
                            pass

                        # label was drawn, so purge from list

                        del theseLabels[labelName]
                i = i + 1

        # Now that all has been done, swap buffers

        if screenBuf == None:
            pygame.display.flip()


############## runScreenEvents ##########################
# This method is used to forward the specified event
# along to all assigned buttons/listeners.
#
# It takes a single argument, eventType, that can currently be
# either "press", "release", or "drag"
#########################################################


def runScreenEvents(eventType):

    # is there a screen definition for the current screen

    if screens.has_key(ci.fcmode):

        # okay, check to see if buttons are defined

        if screens[ci.fcmode].has_key('buttons'):

            # okay buttons are defined, so loop over them and issue the appropriate message

            for (buttonName, buttonVal) in screens[ci.fcmode]['buttons'
                    ].items():
                if eventType == 'setDefaults':

                    # set the default values for any buttons that have "live defaults"

                    try:
                        if hasattr(buttonVal, 'setDefault'):
                            buttonVal.setDefault()
                    except:
                        print sys.exc_info()[0]
                        print sys.exc_info()[1]
                        print sys.exc_info()[2]
                if eventType == 'press':

                    # dispatch the mouse press event to anyone listening

                    try:
                        if hasattr(buttonVal, 'handlePress'):
                            buttonVal.handlePress()
                    except:
                        print sys.exc_info()[0]
                        print sys.exc_info()[1]
                        print sys.exc_info()[2]
                elif eventType == 'release':

                    # dispatch mouse release event

                    try:
                        if hasattr(buttonVal, 'handleRelease'):
                            buttonVal.handleRelease()
                    except:
                        print sys.exc_info()[0]
                        print sys.exc_info()[1]
                        print sys.exc_info()[2]
                elif eventType == 'drag':

                    # dispatch mouse drag event to anyone listening

                    try:
                        if hasattr(buttonVal, 'handleDrag'):
                            buttonVal.handleDrag()
                    except:
                        print sys.exc_info()[0]
                        print sys.exc_info()[1]
                        print sys.exc_info()[2]


############# runScreenState ##########################
#
# Update overlays/etc based on a general state of affairs (busy, active, etc)
#######################################################


def runScreenState(state):
    if state == 'setBusy':

        # clock is going into busy mode

        ci.clockBusy = 1

        # is there a screen definition for the current screen

        if screens.has_key(ci.fcmode):

            # setup the temp buffer to draw on

            myScreen = pygame.display.get_surface()

            # okay, check to see if buttons are defined

            if screens[ci.fcmode].has_key('stateLabels'):

                # okay buttons are defined, so loop over them and issue the appropriate message

                for (labelName, labelVal) in \
                    screens[ci.fcmode]['stateLabels'].items():

                    if state == 'setBusy':

                        # setup default

                        try:
                            if hasattr(labelVal, 'setDefault'):
                                labelVal.setDefault()
                        except:
                            pass

                        # render the label

                        try:
                            if hasattr(labelVal, 'drawLabel'):
                                labelVal.drawLabel(myScreen)
                        except:

                            pass

            # Now that all has been done, swap buffers

            pygame.display.flip()
    elif state == 'clearBusy':

        # clock leaving busy mode

        ci.clockBusy = 0
        initializeScreen()


############## tap_down #################################
# This method is called from the main event loop whenever
# a pygame MOUSEDOWN event is detected.
# It then dispatches the event to the buttons for the current screen
#########################################################


def tap_down():
    runScreenEvents('setDefaults')
    runScreenEvents('press')


############## tap_down #################################
# This method is called from the main event loop whenever
# a pygame MOUSEUP event is detected.
# It then dispatches the event to the buttons for the current screen
#########################################################


def tap_release():
    runScreenEvents('release')


############## tap_drag #################################
# This method is called from the main event loop whenever
# a pygame MOUSEMOTION event is detected.
# It then dispatches the event to the buttons for the current screen
#########################################################


def tap_drag():
    runScreenEvents('drag')


# Done

######################## Done Event Driver/Handlers #############################

########################!!!!!!!!!!!!!!!!!!!!!!!!!!!!#############################
########### Everything below this point is obsolete now #########################
########################!!!!!!!!!!!!!!!!!!!!!!!!!!!!#############################

# ****************************** ABOUT Buttons actions ********************


def aboutbutton():
    ci.fcmode = 1
    ci_clock.clock()


######################## ABOUT Button ############################


def button7():  # ABOUT
    ci.fcmode = 2
    ci_clock.clock()
    ci_gfx.gfx_refresh()


######################## Done ABOUT Button #######################

