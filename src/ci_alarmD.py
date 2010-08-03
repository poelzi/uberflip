#!/usr/bin/python
# -*- coding: utf-8 -*-
#####################################################################
# AlarmD D-Bus Interface Module
#
# By Rob Williams (jolouis) for the FlipClock project
# Provides methodologies for connecting and working with the AlarmD
# daemon over D-Bus. There is a Python wrapper module available to
# allow direct communications with AlarmD using the libalarmd library, but
# D-Bus provides a few extra (very useful) methods, and is the recommended
# way to communicate between applications, which is what you're really doing
# with alarm functionality.
#
# Eventually all of the code from Ciro's original ci_alarm module should
# probably be moved over to here.
#
# AlarmD D-Bus API specs are here:
# http://maemo.org/api_refs/3.0/alarm-api/alarm__dbus_8h-source.html
# http://maemo.org/api_refs/4.0/alarm-api/alarmd-alarm-dbus.html
#
# And of course the howto that explains it all
# http://test.maemo.org/platform/docs/howtos/howto_alarm_interface_bora.html
#
# There is technically (or supposedly) support for an alarmD wrapper in python on Maemo
# as indicated :https://garage.maemo.org/tracker/index.php?func=detail&aid=1544&group_id=40&atid=229
# but it's never been updated so I've utilized the source code, updated it myself and included it as alarmdModule.py
# WEll, actually, for now we'll stick with the native osso one... once I get the alarmdModule updated, then migrate there...
# It still has some short commings, and my understanding of c-wrapping in Python is not up to par to fix it yet
# so for now, we use both the DBus interface, and the alarm module (the native python module is missing
# the "query_event" method which returns a list of events, so I use D-Bus for that one).
#
#
######################################################################

import ci_init as ci

import ci_alarmNew as ci_alarm

import sys
import dbus
import time as myTime
import re

# Import the updated native alarmd module

import osso.alarmd as alarmd

# Import the config module

import ci_config

alarmdDBus = ci.session_bus.get_object('com.nokia.alarmd',
        '/com/nokia/alarmd')

# Define a default set of flags for flipClock alarms

defaultFlags = alarmd.ALARM_EVENT_NO_DIALOG | alarmd.ALARM_EVENT_BOOT \
    | alarmd.ALARM_EVENT_ACTIVATION | alarmd.ALARM_EVENT_SHOW_ICON

# defaultFlags = alarmd.ALARM_EVENT_BOOT | alarmd.ALARM_EVENT_ACTIVATION
# defaultFlags = alarmd.ALARM_EVENT_BOOT | alarmd.ALARM_EVENT_ACTDEAD | alarmd.ALARM_EVENT_SHOW_ICON

# Define a main "alarm template" for the flipclock alarmD service
# This is used as the base for building alarm events, or as the comparison for searching
# for existing "flipclock" alarm events

defaultAlarmTemplate = {}
defaultAlarmTemplate['flags'] = defaultFlags

# defaultAlarmTemplate["sound"] = ci.path+ci.alarmsound

defaultAlarmTemplate['sound'] = ''
defaultAlarmTemplate['dbus_interface'] = ci.dbusSettings['interface']
defaultAlarmTemplate['dbus_service'] = ci.dbusSettings['service']
defaultAlarmTemplate['dbus_path'] = ci.dbusSettings['path']
defaultAlarmTemplate['dbus_name'] = 'triggerAlarm'
defaultAlarmTemplate['title'] = 'Flipclock Alarm'
defaultAlarmTemplate['message'] = ''
defaultAlarmTemplate['snooze'] = 0
defaultAlarmTemplate['recurrence'] = 0
defaultAlarmTemplate['recurrence_count'] = 0  # Once only, or -1 for forever

####################### AlarmD D-Bus interface methods #######################
########################################
# listAlarmIDs()
#
# Arguments: startTime - Seconds since Epoch that you want to use as beginning of search
#            endTime - Seconds since Epoch that you want to use as end of search
# ............ flags - Flags to filter events by. Default setting here should be fine unless you know better.
# Function to return a list of the IDs of all alarms that are currently set on the device. Note
# that these alarms are not all of the ones on the system (alarmD is responsible
# for all time-based events on the tablets, i.e. checking email, checking for updates
# etc, so we don't want to see those).
#
# This is really a helper function for things like counting number of alarms, etc. A full/detailed list
# is retrieved later using this function as a helper.
#
#########################################


def listAlarmIDs(startTime=0, endTime=sys.maxint, flags=defaultFlags):
    theIDs = alarmdDBus.query_event(dbus.UInt64(startTime),
                                    dbus.UInt64(endTime),
                                    dbus.Int32(flags),
                                    dbus.Int32(flags))

    return theIDs


########################################
# listAlarms()
#
# Arguments: filterArr - Dict object used as a filter. Any key/values defined here must match
# ........................the returned alarm objects.
# ............ startTime - Seconds since Epoch that you want to use as beginning of search
#            endTime - Seconds since Epoch that you want to use as end of search
# ............ flags - Flags to filter events by. Default setting here should be fine unless you know better.
# Function to return a detailed list of all of the alarms that are currently set on the device. Note
# that these alarms are not all of the ones on the system (alarmD is responsible
# for all time-based events on the tablets, i.e. checking email, checking for updates
# etc, so we don't want to see those).
#
# This is really a helper function for things like counting number of alarms, etc. A full/detailed list
# is retrieved later using this function as a helper.
#
# Returns an array of Alarm Objects, each being a dict with the following members:
# .... v['cookie']  - Unique identifier for this alarm; passed to delete to clear alarm
#    v['alarm_time'] - Unix timestamp of alarm
#    v['recurrence'] - Int specifing how many minutes between occurances
#    v['recurrence_count'] - Int specifying how many times alarm should occur (-1 for infinate)
#    v['snooze'] - Number of events minute is snoozed; only used with built in clock NOT HERE
#    v['title'] - Title of Alarm; do whatever we want with this
#    v['message'] - Message of Alarm; do whatever we want with this
#    v['sound'] - Sound file for Alarm; we have to play this ourselves
#    v['icon'] - Icon, NOT USED HERE
#    v['dbus_interface'] - Interface of Alarm; should always point to our flipclock dbus interface
#    v['dbus_service'] - Service of Alarm; should always point to our flipclock dbus service
#    v['dbus_path'] - Path to Alarm Service; should always point to our flipclock dbus path
#    v['dbus_name'] - Method path to call; should always point to our flipclock "trigger alarm" method, tho could be given others
# ........................later to make different "Types" of alarms
#    v['flags'] - Controls how alarm is displayed/handled. For us this should always be defaultFlags
#    v['snoozed'] - Shows how many times alarm has been snoozed; doesn't apply to us.
#
#########################################


def listAlarms(
    filterArr=None,
    startTime=0,
    endTime=sys.maxint,
    flags=defaultFlags,
    ):
    print flags

    # start by getting a list of ID's

    alarmIDs = listAlarmIDs(startTime, endTime, flags)

    # Now iterate over and fetch the information for each event

    alarmList = []
    for entry in alarmIDs:
        thisEntryRaw = alarmdDBus.get_event(entry)

        # print thisEntryRaw
    # ....thisEntry = dbusAlarmToPy(thisEntryRaw)

        thisEntry = alarmd.get_alarm(entry)

        # Add the cookie value since it's not returned but useful later...

        thisEntry['cookie'] = entry

        if filterArr != None:

            # filter was passed in, so try to see if this entry matches filter req.

            isValid = compareDicts(filterArr, thisEntry)

            if isValid:

                alarmList.append(thisEntry)
        else:

            # Just add it since no filter supplied

            alarmList.append(thisEntry)

    return alarmList


########################################
# setFlipAlarm()
#
# Arguments: alarmObj - Dict object used to describe an alarm event.
# ........................
# ....The alarmObj needs to have, at minimum, the following properties:....
# .........alarm_time - timestamp indicating when the alarm should occur
# .........recurrence_count - How many times the event should re-occur. Use -1 for infinate times
# .........recurrence - How many minutes should pass between occurances (i.e. once a day = 24 * 60 = 1440 minutes, etc)
# .........title - Title of this alarm
# ....
#
# ............
# Sets a "flipclock alarm event" that will trigger a flipclock handled alarm. Alarms are defined in two stages:
# First, the alarm data is stored in the local config settings file so that it can be read and accessed at the time of occurance;
# secondly, an AlarmD event is added that will trigger the flipclock at the given time; the app will then check it's config file
# for an alarm that matches and execute it.
#
#########################################


def setFlipAlarm(alarmObj):

    # First, check to make sure the alarmObj specified has the required properties....

    if alarmObj.has_key('alarm_time') == 0:
        return False

    # Build out the complete Alarm Dict

    myAlarm = defaultAlarmTemplate
    myAlarm['alarm_time'] = int(alarmObj['alarm_time'])

    for myKey in ['recurrence_count', 'recurrence', 'title']:
        if alarmObj.has_key(myKey):
            myAlarm[myKey] = alarmObj[myKey]

    # Add Alarm to config file
    # print myAlarm

    # alarmd.cancel_alarm(1236108224)

    # Okay, now add Alarm to AlarmD
    # result = alarmd.add_alarm(myAlarm["alarm_time"], myAlarm["recurrence"],  myAlarm["recurrence_count"],  myAlarm["snooze"],  myAlarm["title"],  myAlarm["message"],  myAlarm["sound"], "",  myAlarm["dbus_interface"],  myAlarm["dbus_service"],  myAlarm["dbus_path"],  myAlarm["dbus_name"], myAlarm["dbus_path"],  myAlarm["flags"])

    # # This works, but let's try cleaning up all those dbus declarations...
    # result = alarmdDBus.add_event(dbus.ObjectPath('/AlarmdEvent'), dbus.UInt32(2), dbus.String('action'), dbus.ObjectPath('/AlarmdActionDbus'), dbus.UInt32(7), dbus.String('flags'),dbus.Int32(myAlarm["flags"]), dbus.String('title'), dbus.String(myAlarm["title"]),dbus.String('interface'), dbus.String( myAlarm["dbus_interface"]),  dbus.String('service'), dbus.String( myAlarm["dbus_service"]), dbus.String('path'), dbus.String(myAlarm["dbus_path"]), dbus.String('name'), dbus.String(myAlarm["dbus_name"]), dbus.String('arguments'), dbus.Array([myAlarm["alarm_time"]], signature=dbus.Signature('v')), dbus.String('time'), dbus.Int64(myAlarm["alarm_time"]));

    # Setup the alarm arguments so that they can be passed to the D-Bus add_event method

    action = []
    action.extend(['flags', myAlarm['flags']])
    action.extend(['title', myAlarm['title']])
    action.extend(['interface', myAlarm['dbus_interface']])
    action.extend(['service', myAlarm['dbus_service']])
    action.extend(['path', myAlarm['dbus_path']])
    action.extend(['name', myAlarm['dbus_name']])
    action.extend(['arguments', dbus.Array([myAlarm['alarm_time'],
                  alarmObj['alarm_index']], signature=dbus.Signature('v'
                  ))])

    event = []
    if myAlarm['recurrence_count'] == 0:
        event.extend([dbus.ObjectPath('/AlarmdEvent'), dbus.UInt32(2)])
    else:
        event.extend([dbus.ObjectPath('/AlarmdEventRecurring'),
                     dbus.UInt32(4)])

    event.extend(['action', dbus.ObjectPath('/AlarmdActionDbus')])
    event.append(dbus.UInt32(len(action) / 2))
    event.extend(action)
    event.extend(['time', dbus.Int64(myAlarm['alarm_time'])])

    # #add the extra settings for a recurring event

    if myAlarm['recurrence_count'] != 0:
        event.extend(['recurr_interval',
                     dbus.UInt32(myAlarm['recurrence'])])
        event.extend(['recurr_count',
                     dbus.Int32(myAlarm['recurrence_count'])])

    # All set, perform the actual D-Bus request to add the event with the specified arguments.

    result = alarmdDBus.add_event(*event)

    # success?
    # print myTime.time()

    return result


########################################
# clearFlipAlarm()
#
# Method to delete a given alarmD alarm, based on the supplied argument "cookie"
#
# Arguments: cookie - int indicating the alarmD "cookie" that we want to delete
########################################


def clearFlipAlarm(cookie):

    # Make the D-Bus call to do it

    result = alarmdDBus.del_event(dbus.Int32(cookie))

    return result


########################################
# enableAlarm(alarmIndex)
#
#  Enables a flipclock alarm and makes it active with alarmD. The argument
# alarmIndex is a number indicating which of the existing alarms from ci_config.alarms
# we're talking about; all data is read from that index and the config isupdated
# accordingly
#
#########################################


def enableAlarm(alarmIndex):

    # Try to grab the alarm in question

    success = 0

    if len(ci_config.alarms) >= alarmIndex:

        # error check

        thisAlarm = ci_config.alarms[alarmIndex]

        if int(thisAlarm['alarm_time']) > 0:
            if ci_config.preferences['useAlarmD'] == 1:

                # We want to use alarmD to manage alarms
                # dispatch alarm to alarmD
                # first, check to see if this alarm has been set in the past

                if int(thisAlarm['alarm_cookie']) > 0:
                    clearFlipAlarm(int(thisAlarm['alarm_cookie']))

                # Now we set the new alarm

                returnedCookie = setFlipAlarm(thisAlarm)

                if returnedCookie < 1:

                    # Failed!

                    print 'Failed to set alarm with alarmD!'
                else:
                    ci_config.alarms[alarmIndex]['alarm_cookie'] = \
                        int(returnedCookie)

                    # and now update the prefs array of alarms
                    # ci_config.alarms[alarmIndex]["alarm_cookie"] = returnedCookie

                    ci_config.alarms[alarmIndex]['enabled'] = 1

                    # save the config

                    ci_config.savePrefs()

                    success = 1
            else:

                # We want to manage alarms internally only (Ciro...this is you buddy)

                ci_config.alarms[alarmIndex]['enabled'] = 1

                # save the config

                ci_config.savePrefs()

                success = 1
        else:

            print 'Invalid alarm time, unable to set'
    else:

        print 'No alarm for that index found!'

    # Update "next alarm" incase things have changed

    ci_alarm.nextAlarmUpToDate(1)

    return success


########################################
# disableAlarm(alarmIndex)
#
#  Disables a flipclock alarm and makes it inactive with alarmD. The argument
# alarmIndex is a number indicating which of the existing alarms from ci_config.alarms
# we're talking about; all data is read from that index and the config isupdated
# accordingly
#
#########################################


def disableAlarm(alarmIndex):

    # Try to grab the alarm in question

    success = 0

    if len(ci_config.alarms) >= alarmIndex:

        # error check

        thisAlarm = ci_config.alarms[alarmIndex]

        if ci_config.preferences['useAlarmD'] == 1:

            # We want to use AlarmD to manage alarms

            if int(thisAlarm['alarm_cookie']) > 0:
                result = clearFlipAlarm(int(thisAlarm['alarm_cookie']))

                if result:
                    print 'cleared ok'
                    ci_config.alarms[alarmIndex]['alarm_cookie'] = 0

        ci_config.alarms[alarmIndex]['enabled'] = 0

        # save the config

        ci_config.savePrefs()

        success = 1
    else:

        print 'No alarm for that index found!'

    # Update "next alarm" incase things have changed

    ci_alarm.nextAlarmUpToDate(1)

    return success


######################### disableAllAlarms #####################################################
#
# Do we want this function?... to clear out all alarms... or why not just do a cleanup
# at init time to eliminate alarms that aren't defined in the config file... how about instead we do
#
################################################################################################

######################### findBrokenAlarms #####################################################
#
# Function to scan alarmD settings and remove any alarms that are not defined and enabled in the
# flipclock config...
#
################################################################################################


def findBrokenAlarms():

    # Start by getting a list of all flip alarms from alarmD

    testCond = {}
    testCond['dbus_interface'] = ci.dbusSettings['interface']
    setAlarms = listAlarms(testCond)

    brokenAlarms = []

    for thisAlarm in setAlarms:

        # Now compare this alarm against the defined ones

        valid = 0

        thisDay = ''
        for configedAlarm in ci_config.alarms:
            if configedAlarm['enabled'] == 1:
                if configedAlarm['alarm_cookie'] == thisAlarm['cookie']:
                    valid = 1
                    thisDay = ci.daysList[configedAlarm['alarm_day']]
                    break

        if valid == 0:
            print 'Found invalid alarm at ' + str(thisAlarm)
            brokenAlarms.append(thisAlarm)
        else:
            print 'Alarm for ' + thisDay + ' is valid'

    return brokenAlarms


######################################## Alarm D-BUS Utility functions #########################
# While D-Bus is great, D-Bus interacting with Python... not so great. So in order to actually
# communicate seamlessly we need some conversion functions: one to convert D-BUS alarmD data objects
# into python dict structs, and one to do the opposite. Some other comparison funcs and things
# can also be handy, so they're here as well.

########################################
# dbusAlarmToPy()
#
# Arguments: alarmDetailsRaw - D-Bus Alarm Object to be parsed
#
# Function to take a D-Bus object returned by alarmd.get_alarm D-Bus method
# and convert it into a native Pythong Dict object so that it can be easily used.
#
# Really this should be a better designed, more versatile general D-Bus message parser, but this
# works for now and complies with Maemo 5 preview SDK interfaces, so...
#
#########################################


def dbusAlarmToPy(alarmDetailsRaw):

    thisAlarm = {}
    mainLen = alarmDetailsRaw[1] + 2
    i = 2
    counter = mainLen * 2
    while i < counter:
        thisKey = alarmDetailsRaw[i]
        if thisKey == 'action':

            # Action is a sub-object

            subObj = {}
            subLen = alarmDetailsRaw[i + 2]
            j = i + 3
            while j < i + 2 + subLen * 2:
                subKey = alarmDetailsRaw[j]
                subVal = alarmDetailsRaw[j + 1]

                subObj[subKey] = subVal
                j = j + 2

            thisAlarm[thisKey] = subObj
            counter = counter + subLen * 2 - 2
            i = i + 3 + subLen * 2
        else:

            # not an action

            thisAlarm[thisKey] = alarmDetailsRaw[i + 1]

            i = i + 2
    return thisAlarm


########################################
# pyToDbusAlarm()
#
# Arguments: alarmDetailsObj - Py Dict object describing alarm details to be encoded
#
# Function to take a Pythong Dict object and convert it into a D-Bus object
# that can bereturned by alarmd.get_alarm D-Bus method
# Maybe this isn't the right approach...
#
#########################################


def dbusAlarmToPy(alarmDetailsRaw):
    pass


########################################
# compareDicts()
#
# Arguments: dict1 - Py Dict object to use as required keys/values
# ............ dict2 - Py Dict object to search for matching keys/values in
#
# Function to compares two dicts and returns true if all of the values of dict1 exist
# and match dict2. Primarily used for determining/filtering alarm events to see if they
# line up with events generated by/for this app.
#
#########################################....


def compareDicts(dict1, dict2):
    match = 1

    for (k, v) in dict1.items():
        if dict2.has_key(k) == False:

            # Key doesn't exist, so failed

            match = 0
            break
        else:

            # check to see if sub-match

            if isinstance(v, dict):

                # sub-match

                test = compareDicts(v, dict2[k])
                if test != 1:
                    match = 0
                    break
            else:
                if dict2[k] != v:
                    match = 0
                    break

    return match


