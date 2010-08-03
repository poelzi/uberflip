#!/usr/bin/python
# -*- coding: utf-8 -*-

# bring in dependencies

import pygame
import pygame.event
import pygame.transform
from pygame.locals import *

import os

# init values

import ci_init as ci

# Load the configuration/preferences module

import ci_config

# Load the alarm

import ci_alarmNew as ci_alarm

################### Label class defintions #################
#
#  Part of FlipClock
#
#  Module/classes created by Rob Williams, March 2009
############################################################

################### Label Definitions #########################################

#
# textLabel
#
# A class that takes a piece of text and renders it on the screen whenever
# init is called
#


class textLabel:

    def __init__(
        self,
        targetRect=None,
        textToShow='',
        defaultValue='',
        zIndex=0,
        ):

        # The area that the label should appear at

        self.targetRect = targetRect

        # The text to render

        self.textToShow = textToShow

        # default value

        self.defaultValue = defaultValue

        # should this image be drawn after everything else on screen?

        self.zIndex = zIndex

        # Internal properties

        self.enabled = 1
        self.enableCondition = ''
        self.enableConditionTarget = 1

        self.myScreen = pygame.display.get_surface()

        # default font is "big"

        self.font = ci.flipFonts['big']

        # default colour

        self.textColour = (33, 33, 33)

        # default angle

        self.angle = 0

    # Method to set the text

    def setText(self, newText):
        self.textToShow = newText

    # Method to set the text colour

    def setColour(self, newColour):
        self.textColour = newColour

    # method to set the font to use

    def setFont(self, newFont):
        self.font = newFont

    # Method to set the default angle

    def setAngle(self, newAngle):
        self.angle = newAngle

    # method to enable or disable the button

    def enable(self):
        self.enabled = 1

    def disable(self):
        self.enabled = 0

    def setDefault(self):

        # check to see if we should be enabled or not

        if self.enableCondition != '':
            test = eval(self.enableCondition)

            if test == self.enableConditionTarget:
                self.enabled = 1
            else:
                self.enabled = 0

        if self.defaultValue != '' and self.defaultValue != '0':
            self.textToShow = eval(self.defaultValue)

    # Method to set an enable/disable condition

    def setEnableCondition(self, conditionStr, targetVal=1):
        self.enableCondition = conditionStr
        self.enableConditionTarget = targetVal

    # method to draw the text

    def drawLabel(self, tempBuffer=None):
        if self.enabled == 1:
            if tempBuffer == None:
                thisBuff = self.myScreen
            else:
                thisBuff = tempBuffer

            # Make sure we only redraw the rect we want

            thisBuff.set_clip(self.targetRect)

            # Draw the text

            myLabel = self.font.render('%s' % self.textToShow, True,
                    self.textColour)

            # rotate if angle is defined

            if self.angle != 0:
                myLabel = pygame.transform.rotate(myLabel, self.angle)

            thisBuff.blit(myLabel, (self.targetRect.left,
                          self.targetRect.top))

            # only redraw locally if not using a buffer screen surface........

            if tempBuffer == None:

                # Finally, update only the part of the screen that we've affected

                pygame.display.update(self.targetRect)

            # Okay, done, so make sure the whole screen can be redrawn

            thisBuff.set_clip(ci.screenSize)


#
# imageLabel
#
# A class that takes an image and renders it on the screen whenever
# init is called. Can also support multiple images by adding them to
# the target array
#


class imageLabel:

    def __init__(
        self,
        targetRect=None,
        imagesDict={},
        zIndex=0,
        ):

        # The area that the label should appear at

        self.targetRect = targetRect

        # Dict of images to show based on value

        self.imagesDict = imagesDict

        # default value

        self.defaultValue = ''

        # should this image be drawn after everything else on screen?

        self.zIndex = zIndex

        # Internal properties

        self.currentValue = 0
        self.enabled = 1
        self.enableCondition = ''
        self.enableConditionTarget = 1

        self.myScreen = pygame.display.get_surface()

    # Method to add an image to the array

    def addImage(self, key, image):
        self.imagesDict[key] = image

    # Method to remove an image from the array

    def removeImage(self, key):
        del self.imagesDict[key]

    # method to enable or disable the button

    def enable(self):
        self.enabled = 1

    def disable(self):
        self.enabled = 0

    def setDefault(self):

        # check to see if we should be enabled or not

        if self.enableCondition != '':
            test = eval(self.enableCondition)
            if test == self.enableConditionTarget:
                self.enabled = 1
            else:
                self.enabled = 0

        if self.defaultValue != '':
            self.currentValue = eval(self.defaultValue)

    # Method to set the default string

    def setDefaultCondition(self, defaultCondStr):
        self.defaultValue = defaultCondStr

    # Method to set an enable/disable condition

    def setEnableCondition(self, conditionStr, targetVal=1):
        self.enableCondition = conditionStr
        self.enableConditionTarget = targetVal

    # method to draw the text

    def drawLabel(self, tempBuffer=None):
        goodToGo = 0
        needsRedraw = 0
        if self.enabled == 1:

            # Only draw if there's an image associated with the current value

            if self.imagesDict.has_key(self.currentValue):
                if self.imagesDict[self.currentValue] != '':

                    goodToGo = 1

        if goodToGo:
            if tempBuffer == None:
                thisBuff = self.myScreen
                needsRedraw = 1
            else:
                thisBuff = tempBuffer
                needsRedraw = 0

            # Make sure we only redraw the rect we want

            thisBuff.set_clip(self.targetRect)

            # Draw the image

            thisBuff.blit(self.imagesDict[self.currentValue],
                          (self.targetRect.left, self.targetRect.top))

            # only redraw locally if not using a buffer screen surface........

            if needsRedraw:

                # Finally, update only the part of the screen that we've affected

                pygame.display.update(self.targetRect)

            # Okay, done, so make sure the whole screen can be redrawn

            thisBuff.set_clip(ci.screenSize)


