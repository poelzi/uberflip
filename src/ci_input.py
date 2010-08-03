#!/usr/bin/python
# -*- coding: utf-8 -*-
######################################################################
# Modulo input modifica alarm set 0.011 No Party
# Ciro Ippolito
#   Version 9:44 PM 12/31/2008
######################################################################

import pygame
import time
import ci_alarm
import ci_gfx
import ci_mood
from pygame.locals import *

# from _init import *

import ci_init as ci

# ***************** Pygame *************************************

pygame.init()
h1 = pygame.Rect(28, 88, 107, 207)  # magari riuscire a muovere l'area fuori dalla funzione
h2 = pygame.Rect(130, 88, 107, 207)
m1 = pygame.Rect(260, 88, 107, 207)
m2 = pygame.Rect(365, 88, 107, 207)
alarmswi = pygame.Rect(504, 75, 286, 85)  # Select Rect ALARM SWITCH
mood0 = pygame.Rect(504, 180, 140, 85)
mood1 = pygame.Rect(650, 180, 140, 85)  # ****************************************
exitrect = pygame.Rect(0, 400, 800, 100)
font = pygame.font.SysFont('SwissA', 120)

# ***************** Inizializzazione Grafica *************************************

dovecliccai = 0
mousepos = [
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    ]
pos = 0
dragc = [0, 0]
screen = 0
coordinate_numeri = {
    'ore_decine': (28, 88),
    'ore_unita': (130, 88),
    'minuti_decine': (260, 88),
    'minuti_unita': (365, 88),
    }

###################### Code no longer used, should be removed? ##########################


def tastiera():
    global screen, coordinate_numeri, exitrect, fondo, r, g, b

#  drawkeyboard()

    ci_gfx.drawalarm()
    while True:
        event = pygame.event.wait()
        if event.type == QUIT:
            print 'input is exiting!'
        elif event.type == MOUSEBUTTONDOWN:

      # sys.exit(0)                               #La musica e' finita... gli amici se ne vanno...

            print 'mousebutton down:'
            dovecliccai = click()  # let see where the stupid user clicked
        elif event.type == MOUSEBUTTONUP:
            print 'mousebutton up:'
            x = anddrag(mousepos)
            if x == 1:
                return   # return (moodc)#(sveglia)


###################### Done code no longer used, should be removed? ##########################


def drawkeyboard():
    global numeri, screen, coordinate_numeri


#  screen = pygame.display.get_surface()
#  screen.blit(fondo,(0,0))


def click():
    global mousepos, dragc, pos
    global h1, h2, m1, m2, alarmswi, mood0, mood1, moodc
    pos = pygame.mouse.get_pos()
    mousepos = (
        h1.collidepoint(pos[0], pos[1]),
        h2.collidepoint(pos[0], pos[1]),
        m1.collidepoint(pos[0], pos[1]),
        m2.collidepoint(pos[0], pos[1]),
        alarmswi.collidepoint(pos[0], pos[1]),
        exitrect.collidepoint(pos[0], pos[1]),
        mood0.collidepoint(pos[0], pos[1]),
        mood1.collidepoint(pos[0], pos[1]),
        )
    if mousepos[0]:
        dovecliccai = 1
    elif mousepos[1]:
        dovecliccai = 2
    elif mousepos[2]:
        dovecliccai = 3
    elif mousepos[3]:
        dovecliccai = 4
    elif mousepos[4]:
        dovecliccai = 5  # Alarm switch
    elif mousepos[5]:
        dovecliccai = 6  # Mood Off
    elif mousepos[6]:
        dovecliccai = 7  # Mood On


def mood():
    global g_mood
    print "il mood adesso e':", _init.moodc
    screen.blit(g_mood[_init.moodc], (0, 17))
    screen.blit(g_mood[_init.moodc], (0, 70))
    if _init.sw_led == 1:
        if _init.moodc == 0:

      # ledrgb[]=0,0,0

            r = 0
            g = 0
            b = 0
            ci_alarm.led(r, g, b)
            print r, g, b
        elif _init.moodc == 1:
            r = 250
            g = 125
            b = 0
            ci_alarm.led(r, g, b)
            print r, g, b
        elif _init.moodc == 2:
            r = 0
            g = 0
            b = 250
            ci_alarm.led(r, g, b)
            print r, g, b
        elif _init.moodc == 3:
            r = 250
            g = 0
            b = 0
            ci_alarm.led(r, g, b)
            print r, g, b
        elif _init.moodc == 4:
            r = 250
            g = 0
            b = 125
            ci_alarm.led(r, g, b)
            print r, g, b
    pygame.display.flip()


def taprelease():
    global mousepos, dovecliccai, sveglia
    pos = pygame.mouse.get_pos()
    pp = exitrect.collidepoint(pos[0], pos[1])
    if pp:
        print 'Fuori di qui'
        return 0
    sveglia = anddrag(mousepos)
    screen.blit(numeri[int(sveglia[0])], coordinate_numeri['ore_decine'
                ])  # ORE    (11ma lettera)
    screen.blit(numeri[int(sveglia[1])], coordinate_numeri['ore_unita'])
    screen.blit(numeri[int(sveglia[2])],
                coordinate_numeri['minuti_decine'])  # MINUTI (14ma lettera)
    screen.blit(numeri[int(sveglia[3])],
                coordinate_numeri['minuti_unita'])
    pygame.display.flip()


