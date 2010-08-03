#!/usr/bin/python
# -*- coding: utf-8 -*-

#############################################################################
#  FLIP module   0.1.3                                                      #
#  Flipping animation                                                       #
#  Ciro Ippolito                                                            #
#                                                                           #
#   20.00  02/26/2009                                                       #
#############################################################################

import ci_init as ci
import pygame
from pygame.locals import *

# import ci_alarm


def flipping_elem_all_clock(elem, delay):
    for key in ['ore_decine', 'ore_unita', 'minuti_decine',
                'minuti_unita']:
        flipping_element(elem, ci.cl_coords[key], delay)


def flipping_element(elem, position, delay):
    ci.cl_screen.blit(elem, position)  # stampo
    pygame.display.flip()  # mostro
    pygame.time.delay(delay)  # aspetto


def flippingout():  # Just for fun Opening flipping animation
    delay = 0
    for x in range(0, 9):
        for elem in [ci.cl_numeri[x], ci.s1, ci.s2, ci.s3]:
            flipping_elem_all_clock(elem, delay)


def flipclock():  # Flip according to the clock events
    if ci.fcmode == ci.FCMODE_CLOCK:
        for elem in [ci.cl_numeri[int(ci.orario[15])], ci.s1, ci.s2,
                     ci.s3]:
            flipping_element(elem, ci.cl_coords['minuti_unita'], 25)
            if int(ci.orario[15]) == 0:
                flipping_element(elem, ci.cl_coords['minuti_decine'],
                                 25)
                if int(ci.orario[14]) == 0:
                    flipping_element(elem, ci.cl_coords['ore_unita'],
                            25)


