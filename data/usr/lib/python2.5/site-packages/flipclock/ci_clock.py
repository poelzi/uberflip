######################################################################
# Modulo ci_clock 0.1.0 Manage all the clock/alarm/setting functions
#
# Ciro Ippolito
#
# Updated by Rob Williams (jolouis) on
# 20.00 03/04/2009
######################################################################
import ci_gfx
import ci_init as ci
import ci_alarmNew as ci_alarm
import time
import ci_flip

#Import Config options
import ci_config

#import events
import ci_eventsNew as ci_events



if ci.animation:  import ci_flip

def init_app():
	ci_config.setAllNight(int(ci_config.preferences["allNight"]))
	
	
	
	ci_gfx.bg_clock()
	#Only draw animations if using standard flip theme
	if ci.fcmode==ci.FCMODE_CLOCK: 
		if ci.animation:  ci_flip.flippingout()
	ci.orario=time.ctime()              # .ctime instead of .locatime        Ritorna: 'DAY MON DA OR:MI:SE YEAR'
	ci.hou_min=int(ci.orario[11])*600+int(ci.orario[12])*60+int(ci.orario[14])*10+int(ci.orario[15])
	
	#ci_gfx.drawcountdown()
	clock()
	if ci.sw_led==1:  ci_alarm.carnevale() 
	 
def init_clock():
  ci_gfx.drawclock()
  if ci.sw_led==1:  ci_alarm.carnevale()  
  ci.pygame.display.flip()
def clock(buffer = None):
  
  bufferedDisplay = 1
  if (buffer == None):
	buffer = ci.pygame.display.get_surface()
	bufferedDisplay = 0
	
  ci.day = time.strftime("%w", time.localtime())        #0=Sunday
  ci.orario=time.ctime()              # .ctime instead of .locatime        Ritorna: 'DAY MON DA OR:MI:SE YEAR'
  ci.hou_min=int(ci.orario[11])*600+int(ci.orario[12])*60+int(ci.orario[14])*10+int(ci.orario[15])

  ############################### UPDATED BY ROB ##################################
  # Fixed midnight bug, moved AM/PM calculation to here instead of gfx to simplify and eliminate duplicate code
  #Draw 12 Hour mode instead of 24 hour
  #if (ci.sw_config[1] == 0):
  if (ci_config.preferences["militaryTime"] == 0):
	hours = (int(ci.orario[11]) * 10) + int(ci.orario[12])
	ci.isPM = 0
	if (hours > 11):
		ci.isPM = 1
	if (hours == 0):
		hours = 12
	if (hours > 12):
		hours = hours - 12

	
	ci.timeDigits = str(hours)
  	if (hours < 10):
		ci.timeDigits = "0" + ci.timeDigits
  else:
	ci.timeDigits = ci.orario[11] + ci.orario[12] 
  
  ci.timeDigits = ci.timeDigits + ci.orario[14] + ci.orario[15]
  
  ############################## DONE UPDATED BY ROB ##############################

  ######################## UPDATED BY ROB ######################################
  #
  # WE don't need to redraw everything all the time... just the parts that change.
  # Here, since the clock() method is called based on a timeout, we only redraw
  # parts of screens that are clock/time based... everything else can be
  # redrawn based on interaction and events...
  print "clock!!!!!"
  print ci.fcmode
  print ci.FCMODE_CLOCK
  if ci.fcmode==ci.FCMODE_CLOCK or ci.fcmode==ci.FCMODE_NIXIE:                      #***clockMode ********************************
    ci_events.initializeScreen(buffer)
    ci_gfx.drawclock(buffer)

    if (bufferedDisplay == 0):
    	ci_gfx.gfx_refresh()

	              
  elif ci.fcmode==ci.FCMODE_ALARM_CONTROL:                    #ALARM*******************************
    pass

  elif ci.fcmode==ci.FCMODE_ABOUT:                    #ABOUT********************************
    ci_gfx.bg_about()
    if ci.tablet==1:      ci.hildon.hildon_play_system_sound(ci.path+ci.alarmsound)
    ci_gfx.gfx_refresh()
  elif ci.fcmode==ci.FCMODE_WINDOW:                    #WINDOW********************************
    ci_gfx.bg_windo()
    ci_gfx.drawdate()
    ci_gfx.drawsveglia()

    ci_gfx.changecaption()

    ci_gfx.drawwindo() 
  elif ci.fcmode==ci.FCMODE_NIGHT:            #its business (night) time

    ci_events.initializeScreen(buffer)
    ci_gfx.drawnight(buffer)
    if (bufferedDisplay == 0):
    	ci_gfx.gfx_refresh()

#  elif ci.fcmode==5:          #Alarm playing
#  	#### This never occurs #####
#    ci_gfx.bg_clock()
#    ci_gfx.drawclock()
#    ci_gfx.drawdate()
#    ci_gfx.drawsveglia()
#    ci_gfx.drawmood()
#    ci_gfx.gfx_refresh()
  return

def alarm():
  alarm=[0,0,0,0]
  alarm[0:4] = ci.alarms[ci.al_set]

def conv_min2est(min):
  est=[0,0,0,0]
  est = [(ci.ala_min/600),
         (ci.ala_min%600)/60,
         (ci.ala_min%60)/10,
         (ci.ala_min%60)%10]
  return est

def conv_est2min():
  pass
