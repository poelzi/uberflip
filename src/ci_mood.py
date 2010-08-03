#!/usr/bin/python
# -*- coding: utf-8 -*-
import ci_init as ci
import ci_alarm

#############################################################################
#  MOOD module   0.005                                                      #
#  (worste code ever) EDIT: getting better thanks to Faheem Pervez and PLOP #
#     31/12/2008                                                            #
#   Developers:                                                             #
#   Ciro Ippolito - Faheem Pervez                                           #
#############################################################################
# ****************** Mood Things


def mood():
    ci.cl_screen.blit(ci.mood_col[ci.moodc], (0, 17))  # top light
    if ci.fcmode == 0:
        ci.cl_screen.blit(ci.mood_col[ci.moodc], (0, 380))  # bottom light
    else:
        ci.cl_screen.blit(ci.mood_col[ci.moodc], (0, 70))  # bottom light
    if ci.tablet:
        moodtablet()  # Led


#  else:
#    #[DEBUG]print "moodc",ci.moodc
#    mood_pc()        #Noled


def moodtablet():
    if ci.moodc == 0:
        ci.r = 0
        ci.g = 0
        ci.b = 0
    elif ci.moodc == 1:
        ci.r = 250
        ci.g = 125
        ci.b = 0
    elif ci.moodc == 2:
        ci.r = 0
        ci.g = 0
        ci.b = 250
    elif ci.moodc == 3:
        ci.r = 250
        ci.g = 0
        ci.b = 0
    elif ci.moodc == 4:
        r = 250
        g = 0
        b = 125
    ci_alarm.led()


def mood_pc():
    ci.cl_screen.blit(ci.mood_col[ci.moodc], (0, 17))  # top light
    if ci.fcmode == 0:
        ci.cl_screen.blit(ci.mood_col[ci.moodc], (0, 380))  # bottom light
    else:
        ci.cl_screen.blit(ci.mood_col[ci.moodc], (0, 70))  # bottom light


