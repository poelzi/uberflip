#####################################################################
# FlipClock Config Controller Module
#
# By Rob Williams (jolouis) for the FlipClock project
# Provides the flipclock Configuration control functions
# Including reading the config file, storing settings, writing, etc
# 
# March 4, 2009
# 
######################################################################

import os
try:
	import osso
except ImportError:
	osso = None
import ConfigParser


#cPickle module for data serialization
import cPickle as pickle

#copy module, needed for element copying
import copy

#Import gconf settings for "all night" mode
try:
    import gnome.gconf as gconf
except:
    import gconftool as gconf


import ci_init as ci

#File to store config data in
configFile = ci.userpath + ".flipclock.conf"

#config parser object representing stored data
currentConfig = ConfigParser.ConfigParser()

#current settings (with defaults)
preferences = {}
preferences["militaryTime"] = 0    			#Default setting is to use AM/PM mode.
preferences["mood"] = 0    		   			#Default mood is 0 (no mood).
preferences["theme"] = ci.FCMODE_CLOCK		#Default "view" is regular flip clock
preferences["allNight"] = 1					#Should dim-time to be extended to a huge number so display stays "semi-light" all night?
preferences["alarmDSnooze"] = 0				#Should alarmD be used for snoozing, or do it internally? 0 = internal, 1 = alarmD
preferences["useAlarmD"] = ci.tablet		#default is use alarmD if running on tablet

############ Alarms###########
# For now until Ciro comes up with a different alarm control interface, we're going to stick with
# 7 pre-defined alarms that you can turn on/off. 

# Alarm event template, as required by ci_alarmD.py
alarmObjTemplate = {}
alarmObjTemplate["alarm_time"] = 0
alarmObjTemplate["alarm_index"] = 0				#Unique index for this alarm, used to match dbus signal with configured alarms
alarmObjTemplate["alarm_hhmm"] = "0000"
alarmObjTemplate["ampm"] = 1					#Am = 1, PM = 0
alarmObjTemplate["alarm_day"] = 0				 #What day of the week does this alarm represent? Temporary until Ciro gives us a date picker...
alarmObjTemplate["alarm_cookie"] = 0				 #Unique cookie/index of this alarm
alarmObjTemplate["title"] = "Flipclock Alarm"    #Increment this as we add it to the array
alarmObjTemplate["recurrence_count"] = -1        #Always happen unless it gets turned off
alarmObjTemplate["recurrence"] = (60 * 24 * 7)   #Once per week, so alarm always happens on the same day
alarmObjTemplate["enabled"] = 0					 #Alarm is disabled by default
alarmObjTemplate["sound"] = ci.path + ci.alarmsound #Default alarm sound
alarmObjTemplate["alertMode"] = 1					#Default alert mode (play sound); other options could be added later for party mode, etc
alarmObjTemplate["loopSound"] = 0				 #should the sound file be looped, or just play once?
alarmObjTemplate["snoozeTime"] = 10				 #Number of minutes to snooze for this alarm


#Currently defined alarms
alarms = []
for i in range(7):
	thisAlarm = copy.deepcopy(alarmObjTemplate)
	thisAlarm["alarm_day"] = i 
	thisAlarm["alarm_index"] = i
	thisAlarm["title"] = thisAlarm["title"] + " " + str(i + 1)
	alarms.append(thisAlarm)


#####################################################################
# loadPrefs
#
# Function to load the configuration data from an existing config file (if it exists)
# and set the user preferences/etc
#
#####################################################################

def loadPrefs():
	global preferences
	global alarms
	global currentConfig
	
	if os.path.exists(configFile):
		try:
			currentConfig.read(configFile)
			#Try to load the preferences first
			if (currentConfig.has_section("Main Options")):
				#Check for 12 or 24 hour mode
				if (currentConfig.has_option("Main Options", "militaryTime")):
					preferences["militaryTime"] = int(currentConfig.get("Main Options", "militaryTime"))
					
				#Check for mood
				if (currentConfig.has_option("Main Options", "mood")):
					preferences["mood"] = int(currentConfig.get("Main Options", "mood"))
					
				#Check for theme
				if (currentConfig.has_option("Main Options", "theme")):
					preferences["theme"] = int(currentConfig.get("Main Options", "theme"))
					
					#quick error check to account for changes in theme organization
					if (preferences["theme"] < ci.FCMODE_CLOCK):
						preferences["theme"] = ci.FCMODE_CLOCK
					
				#Check for allNight
				if (currentConfig.has_option("Main Options", "allNight")):
					preferences["allNight"] = int(currentConfig.get("Main Options", "allNight"))
					
				#Check for alarmDSnooze
				if (currentConfig.has_option("Main Options", "alarmDSnooze")):
					preferences["alarmDSnooze"] = int(currentConfig.get("Main Options", "alarmDSnooze"))
					
				#Check for useAlarmD
				if (currentConfig.has_option("Main Options", "useAlarmD")):
					preferences["useAlarmD"] = int(currentConfig.get("Main Options", "useAlarmD"))
			
			#Read Alarm array/settings if present...
			if (currentConfig.has_section("Alarms")):
				if(currentConfig.has_option("Alarms", "alarmDict")):
					#Read the pickle'd dict object from the config file
					newAlarmsRaw = currentConfig.get("Alarms", "alarmDict");
					
					#convert the pickle'd string back to it's alarm[] nested list
					alarms = pickle.loads(newAlarmsRaw)		
			
  		except:
			osso_c = osso.Context("osso_test_note", "0.0.1", False)
			note = osso.SystemNote(osso_c)
			result = note.system_note_dialog("Can't read config", type='notice') 
			print result

	#No need for a default configuration


	#Apply loaded config to global vars as required
	if (preferences.has_key("militaryTime")):
		ci.sw_config[1] = preferences["militaryTime"]




#####################################################################
# savePrefs
#
# Function to save the current preferences back to the config file
#
#####################################################################

def savePrefs():
	global preferences
	global alarms
	global currentConfig
	
	#Only save if the config actually changed...
	configChanged = 0
	
	#Check to see if config file exists, and create it if not
	if (os.path.exists(configFile) == 0):
		print "no config file"
		try:
			f = open(configFile, 'w')
			#Set to globally read/write just to be safe
			os.chmod(configFile, 0777)
			
			f.close()
		except:
			osso_c = osso.Context("osso_test_note", "0.0.1", False)
			note = osso.SystemNote(osso_c)
			result = note.system_note_dialog("Can't create config file", type='notice') 
			return False
	
	#Now save it
	##################### Save Main Options ###########################
	if (currentConfig.has_section("Main Options") == 0):
		#Create the main config section
		currentConfig.add_section("Main Options")
		
		#added a section, so definitely changed
		configChanged = 1

	for k,v in preferences.items():
		if (currentConfig.has_option("Main Options", k)):

			if (currentConfig.get("Main Options", k) != str(v)):
				currentConfig.set("Main Options", k, str(v))
				#value didn't match, so changed
				configChanged = 2
		else:
			currentConfig.set("Main Options", k, str(v))
				
			#value didn't exist, so changed
			configChanged = 3
		
				
	###################### Done Main Options ##########################

	###################### Save Alarm Settings ########################
	if (currentConfig.has_section("Alarms") == 0):
		#Create the alarms config section
		currentConfig.add_section("Alarms")
		
		#added a section, so definitely changed
		configChanged = 4
	
	if (currentConfig.has_option("Alarms", "alarmDict") == 0):
		print "Adding alarms"
		#Store the alarms list as a pickle'd string
		currentConfig.set("Alarms", "alarmDict", pickle.dumps(alarms))
		
		#added alarms, so definitely changed
		configChanged = 5	
	else:
		print "pre comparing and updating alarms"
		#check to see if stored alarms match current alarms
		if (pickle.loads(currentConfig.get("Alarms", "alarmDict")) != alarms):
			print "comparing and updating alarms"
			
			#Stored alarms don't match
			#Store the alarms list as a pickle'd string
			currentConfig.set("Alarms", "alarmDict", pickle.dumps(alarms))
			
			#added alarms, so definitely changed
			configChanged = 6	
			
			
	if (configChanged > 0 ):
		##DONE, now save it
		f = open(configFile , 'w')
		currentConfig.write(f)
		f.close()
	
	return configChanged
			
	

################## Preference-related helper functions ###############################

######### setAllNight ########################################
#
# function to set clock into allNight mode or not. Accepts
# a single argument, 1 or 0, indicating new setting. Passing
# no argument causes mode to be toggled.
#
##############################################################

def setAllNight(newMode= None):
	global preferences
	#setup dim mode if needed
	client = gconf.client_get_default()
	if (ci.originalDim == -1):
		ci.originalDim = client.get_int("/system/osso/dsm/display/display_blank_timeout")
	
	if (newMode == None):
		if (int(preferences["allNight"]) == 0):
			newMode = 1
		else:
			newMode = 0
			
		preferences["allNight"] = newMode
		#save updated preferences since we've toggled them; otherwise save must be called manually.
		savePrefs()
		
	
	if (newMode == 1):
		#Set the dimtime to 1 day... that should do the trick!
		#and we then don't have to worry about chargers or anything since inactivity flag is only raised if screen actually goes off!
		client.set_int("/system/osso/dsm/display/display_blank_timeout", 24 * 3600)
		
		ci.dimChanged = 1
		print "Set Dim"
	else:
		#and we then don't have to worry about chargers or anything since inactivity flag is only raised if screen actually goes off!
		client.set_int("/system/osso/dsm/display/display_blank_timeout", ci.originalDim)
		
		ci.dimChanged = 1
		print "Cleared Dim"
		
	return newMode




