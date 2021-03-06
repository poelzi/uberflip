#!/usr/bin/python
# -*- coding: utf-8 -*-
import pygame.base  # trying to minimize the pygame's modules number
import pygame.event
import pygame
import os
import time
import ConfigParser

from datetime import date

# Option parser for CLI options

from optparse import OptionParser

import dbus
import gobject

try:
    import osso
except ImportError:
    osso = None
from dbus.mainloop.glib import DBusGMainLoop

######################################################################
# Flipclock 0.2.1 Inizializzazione variabili generiche
# Ciro Ippolito ciron810@gmail.com
# Updated by Rob Williams (jolouis) for dbus handling
#  20.00 - 04/03/2009
######################################################################

os.environ['SDL_VIDEO_X11_WMCLASS'] = 'flipclock'
os.environ['SDL_AUDIODRIVER'] = ''  # to trick pygame and make it believe I dont have an audio hardware
tablet = 0  # Im not sure if this still have sense...
sw_led = 1  # 0=disable 1=enable
animation = 1  # set 1 to enable animations (flipping, scrolling)

userpath = os.path.expanduser('~')
if tablet == 1:
    path = '/usr/share/flipclock/'  # unix path (dont forget the '/' at the end)
else:

    # userpath=os.path.expanduser("~")         #BAD BOY PYTHON! BAD BOY!

    path = os.path.join(os.path.dirname(__file__), os.path.pardir,
                        'share', 'flipclock')  # sloppy local ./data/ path

    # userpath="../../../../share/flipclock/"


def theme(suffix):

    # fixme

    return os.path.join(path, suffix)


######################## Command Line Options ########################
#
######################################################################

usage = 'usage: %prog [options] arg'
cliParser = OptionParser(usage=usage, version='0.2.1', prog='FlipClock')

cliParser.set_defaults(fixAlarms=False)
cliParser.add_option('-f', '--fix-alarms', action='store_true',
                     dest='fixAlarms',
                     help='Scan and attempt to clear any erronious Flipclock alarms.'
                     )

(cliOptions, cliArgs) = cliParser.parse_args()

######################## Done Command Line Options ###################

######################## Added by Rob 02/27/09 #######################
# Dbus initialization/handling
######################################################################
# Setup DBus to use the gobject loop as its event loop

DBusGMainLoop(set_as_default=True)

# connect to the session bus

session_bus = dbus.SessionBus()

# establish the main loop........

loop = gobject.MainLoop()

## Define D-Bus Interfaces (for listening on later)

dbusSettings = {}
dbusSettings['interface'] = 'org.maemo.flipclock'
dbusSettings['service'] = 'org.maemo.flipclock'
dbusSettings['path'] = '/org/maemo/flipclock/controller'

# Establish OSSO context and device controls

if osso:
    osso_c = osso.Context('flip_context', '0.1.5', False)
    device = osso.DeviceState(osso_c)

######################### Done DBUS init #############################

# path="data/"                       #sloppy local ./data/ path

# svegliaswitch=0                 #Alarm set default off
# miltimeswitch=0                 #Military time Default off

al_set = 0
alarmsound = 'ringer.mp3'  # To play the control panel/system sounds must be ON
alarm = [0, 0, 0, 0]
all_min = 0  # Allarmset in minutes
ala_min = 0
sveglia = [0, 7, 3, 0]  # Default alarm: 07.30
all_edi = [0, 7, 3, 0]  # Alarm attualemte modificabile
al_edi = [0, 0, 0, 0]  # Alarm attualemte modificabile
bt_aledit = 0  # ok,ok, I know I need to modify all this crappyalarmvars
remaing = [0, 0, 0, 0]  # Countdown variable

pygame.init()
pygame.display.set_caption('Flip Clock 0.2.4 Nixie')
if tablet == 1:
    screenSize = pygame.Rect(0, 0, 800, 480)

    try:
        window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    except:
        window = pygame.display.set_mode((800, 480))
else:
    window = pygame.display.set_mode((800, 480))

################### ROB UPDATE ###############

timeDigits = 0  # Digits for time (HHMM)
isPM = 0  # Is time AM or PM

inactive = 0  # is system inactive or not?
charging = 0  # is system connected to AC or not?

clockBusy = 0  # is the app trying to do something...

# Define a list of days of the week for display purposes

daysList = [
    'Sun',
    'Mon',
    'Tues',
    'Wed',
    'Thurs',
    'Fri',
    'Sat',
    ]

# Define possible clock mode constants

(
    FCMODE_ALARM_CONTROL,
    FCMODE_ABOUT,
    FCMODE_WINDOW,
    FCMODE_CLOCK,
    FCMODE_NIGHT,
    FCMODE_NIXIE,
    ) = range(6)

# Buffer to draw against before displaying

screenBuffer = pygame.display.get_surface()

# Is alarm running or not

alarmRunning = 0

# indicates the alarm day that's currently being selected
# default is Sunday (0)
# try to set the default to today... unfortunately Python's a bit odd in that it considers monday 0, but...

thisDay = date.today().weekday() + 1
if thisDay == 7:

    # sunday

    thisDay = 0

currentAlarmNum = thisDay

# global flag to prevent multiple file choosers from being opened by accident/etc

modalOpen = 0

# Original dim time value, used for restoring from "all night" mode

originalDim = -1
dimChanged = 0

################### DONE ROB UPDATE ##########

hou_min = 0  # time in minutes
fcmode = FCMODE_CLOCK  # 0=clock - 1=alarmset - 2=about - 3=window - 4=night
moodc = 0  # 0=off 1=yellow 2=blue 3=red 4=purple
sw_help = 0
r = 0  # Actual Led color RGB
g = 0  #
b = 0  #
mr = 0  # Color mood color RGB
mg = 0  #
mb = 0  #
orario = 0  # Each module need to know the time!!

sv_coords = [87, 400, 233, 402]  # alarmset , remainingtimeset
date_coords = [293, 395, 291, 417]  # Day/daydate , month/year

# ******* Inizializzazione grafica CLOCK Fullscreeen*****************

cl_coords = {
    'ore_decine': (4, 21),
    'ore_unita': (194, 21),
    'minuti_decine': (416, 21),
    'minuti_unita': (605, 21),
    }
cl_screen = pygame.display.get_surface()
cl_numeri = [pygame.image.load(theme('%s.png' % str(x))) for x in
             range(18)]  # load the 10 digits __thanks PLOP
cl_bground = pygame.image.load(theme('fondo.png')).convert()  # Background
s1 = pygame.image.load(theme('semi1.png')).convert()  # Frame1 flipanim
s2 = pygame.image.load(theme('semi2.png')).convert()  # Frame2 flipanim
s3 = pygame.image.load(theme('semi3.png')).convert()  # Frame3 flipanim

# *********Inizializzazione grafica ALARM Fullscreeen*****************

al_coords = {
    'ore_decine': (28, 109),
    'ore_unita': (130, 109),
    'minuti_decine': (258, 109),
    'minuti_unita': (358, 109),
    }
al_screen = pygame.display.get_surface()
al_bground = pygame.image.load(theme('fondoalarmB.png'))
al_base = pygame.image.load(theme('base.png'))
al_numeri = [pygame.image.load(theme('a' + str(x) + '.png')) for x in
             range(10)]  # load the 10 digits __thanks PLOP

al_switch_coords = [  # posx,posy,x,y,pos_on,pos_off  #Alarm SWITCH
    664,
    91,
    102,
    70,
    588,
    658,
    ]

################### UPDATED BY ROB ##############################
# Place masks and actual switch images in two different lists

switch_masks = {}
switch_masks['alDark'] = pygame.image.load(theme('onoff.png'))  # Dark (normal) switch mask
switch_masks['alMed'] = pygame.image.load(theme('onoffMaskMed.png'))  # Medium switch mask
switch_masks['alLight'] = pygame.image.load(theme('onoffMaskLight.png'))  # Dark (normal) switch mask

switch_images = {}
switch_images['onoff'] = pygame.image.load(theme('onoff1.png'))  # Switch on/off
switch_images['1224'] = pygame.image.load(theme('1224.png'))  # Switch for 12/24 hour
switch_images['ampm'] = pygame.image.load(theme('ampm.png'))  # Switch for AM/PM setting
switch_images['loop'] = pygame.image.load(theme('loopSwitch.png'))  # Switch for loop/once setting

flipFonts = {}
flipFonts['big'] = pygame.font.Font(theme('nosnb.ttf'), 43)  # BIG Font, for Alarm Screen labels
flipFonts['small'] = pygame.font.Font(theme('nosnb.ttf'), 20)  # Small Font, for Alarm Screen labels

alarmIcons = {}
alarmIcons['on'] = pygame.image.load(theme('alarmIconOn.png'))  # Small green icon to say alarm is active
alarmIcons['off'] = pygame.image.load(theme('alarmIconOff.png'))  # Small red icon to say alarm is off
alarmIcons['selected'] = pygame.image.load(theme('alarmChooserOn.png'))  # Box to indicated selected alarm
alarmIcons['nonSelected'] = \
    pygame.image.load(theme('alarmChooserOff.png'))  # Semi-transparent to indicate non-selected

buttonImages = {}
buttonImages['waitScreen'] = pygame.image.load(theme('waitScreen.png'
        )).convert_alpha()  # The "Wait" screen
buttonImages['snoozeBG'] = pygame.image.load(theme('snoozeBox.png'
        )).convert_alpha()  # The big old "snooze" button

moods = [
    {
        'name': 'Off',
        'image': pygame.image.load(theme('m_0.png')),
        'color': (0, 0, 0),
        'nightColor': (0, 0, 250),
        },
    {
        'name': 'Yellow',
        'image': pygame.image.load(theme('m_yello.png')),
        'color': (250, 125, 0),
        'nightColor': (250, 200, 0),
        },
    {
        'name': 'Blue',
        'image': pygame.image.load(theme('m_blue.png')),
        'color': (0, 0, 250),
        'nightColor': (0, 0, 250),
        },
    {
        'name': 'Red',
        'image': pygame.image.load(theme('m_red.png')),
        'color': (250, 0, 0),
        'nightColor': (240, 0, 0),
        },
    {
        'name': 'Purple',
        'image': pygame.image.load(theme('m_purpl.png')),
        'color': (250, 0, 125),
        'nightColor': (220, 0, 160),
        },
    {
        'name': 'Green',
        'image': pygame.image.load(theme('m_green.png')),
        'color': (0, 250, 0),
        'nightColor': (0, 220, 0),
        },
    ]

############ Nixie related stuff

nx_coords = {
    'ore_decine': (4, 21),
    'ore_unita': (194, 21),
    'minuti_decine': (416, 21),
    'minuti_unita': (605, 21),
    }

# FIME use themes
# nx_numeri = [pygame.image.load(theme("nixie/%s.png" %str(x))) for x in range(10)]    #load the 10 digits __thanks PLOP
# nx_bground = pygame.image.load(theme("nixie/fondo.png")).convert_alpha()         #Background

########## these should be redundant now...

onoff_switch = [pygame.image.load(theme('onoff.png')),
                pygame.image.load(theme('onoff1.png')),
                pygame.image.load(theme('1224.png'))]  # Alarm Switch graphics mask
                                                       # Switch on/off
                                                       # switch military time 12/24

mt_switch_coords = [  # posx,posy,x,y,pos_on,pos_off  #MTime SWITCH
    664,
    194,
    102,
    70,
    588,
    658,
    ]

# onoff_switch =[pygame.image.load(path+"onoff.png"),    #12/24 Switch graphics
#               pygame.image.load(path+"onoff1.png")]   #

##### Not needed anymore... #############

sw_config = [0, 0]  # 1.alarm - 2.military

sw_coords = [(664, 91, 102, 70), (664, 194, 102, 70), (584, 31, 102,
             70), (584, 134, 102, 70)]  # SETTING alarm switch
                                        # SETTING military switch
                                        # WINDOW  alarm switch
                                        # WINDOW  military switch

# ******* Inizializzazione grafica CLOCK NIGHT mode*****************

ni_coords = {
    'ore_decine': (42, 61),
    'ore_unita': (206, 61),
    'minuti_decine': (455, 61),
    'minuti_unita': (616, 61),
    }
ni_screen = pygame.display.get_surface()
ni_numeri = [pygame.image.load(theme('n' + str(x) + 'B.png')) for x in
             range(10)]  # load the 10 digits __thanks PLOP
ni_bground = pygame.image.load(theme('fondonightB.png')).convert_alpha()  # Background

# ******* Inizializzazione grafica ABOUT Dullscreen*****************

ab_screen = pygame.display.get_surface()
ab_bground = pygame.image.load(theme('about.png'))
mood_bas = pygame.image.load(theme('aboutlight.png'))  # Green aboutlight

# ******* Inizializzazione grafica WINDOW*****************

wi_screen = pygame.display.get_surface()
wi_bground = pygame.image.load(theme('fondowindo.png'))

# ******* Inizializzazione grafica HELP *****************

gr_help = [pygame.image.load(theme('help' + str(x) + '.png')) for x in
           range(4)]

# ***Inizializzazione pygame generic variables***
# FIXME: fullscreen
# pygame.display.toggle_fullscreen()              #Full screen on

if tablet == 1:  # Hide the mouse pointer
    pygame.mouse.set_visible(0)
try:
    font = pygame.font.Font(theme('nosnb.ttf'), 43)  # Boldish font for the alarm/date
    font1 = pygame.font.Font(theme('nosnb.ttf'), 20)  # small   font for the alarm/date
except:
    print "Can't load fonts"

# ***TABLET's MODEL QUERY***

if tablet == 1:
    import osso
    import hildon
    component_version = file('/proc/component_version', 'r')
    product = component_version.readline()[12:17]
    if product == 'RX-44':  # ***NOKIA N810
        sw_led = 1  # 0=disable 1=enable
        sw_lux = 1  # 0=disable 1=enable
    elif product == 'RX-34':

                               # ***NOKIA N800

        sw_led = 0  # 0=disable 1=enable
elif tablet == 0:
    sw_led = 0  # 0=disable 1=enable
    sw_lux = 0  # 0=disable 1=enable

#  window = pygame.display.set_mode((800,480),pygame.FULLSCREEN)

    window = pygame.display.set_mode((800, 480))

# ***USER WALLPAPER***

userbg = ''
try:
    config = ConfigParser.ConfigParser()
    config.read(userpath + '/.osso/hildon-desktop/home-background.conf')
    userbg = config.get('Hildon Home', 'BackgroundImage')

    if len(userbg) > 0:
        userbg = userbg.replace('file://', '')

      # replace spaces

        userbg = userbg.replace('%20', ' ')
        us_bground = pygame.image.load(userbg).convert()  # Background user
    else:

      # No BG, so go for solid colour instead

        bgRed = float(config.get('Hildon Home', 'Red')) * (255.0
                / 65535.0)
        bgGreen = float(config.get('Hildon Home', 'Green')) * (255.0
                / 65535.0)
        bgBlue = float(config.get('Hildon Home', 'Blue')) * (255.0
                / 65535.0)
        us_bground = pygame.Surface((800, 480))
        us_bground.fill((bgRed, bgGreen, bgBlue))
except:
    if len(userbg) > 0:
        if tablet == 1 and osso:
            osso_c = osso.Context('osso_test_note', '0.0.1', False)
            note = osso.SystemNote(osso_c)
            result = \
                note.system_note_dialog("Can't read the user wallpaper"
                    , type='notice')
            print result

  # Use default background

    us_bground = pygame.image.load(theme('sosbg.png')).convert()
