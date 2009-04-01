
#bring in dependencies

import pygame
import pygame.event
from pygame.locals import *

#init values
import ci_init as ci

#Load the configuration/preferences module
import ci_config


################### Button class defintions #################
#
#  Part of FlipClock
#
#  Module/classes created by Rob Williams, March 2009
############################################################

################## Button class definitions ####################################
# Buttons come in one of three flavours thus far:
# clickButton - Triggered by a press and release over the same area
# dragButton - Triggered by a press and drag-release (released in a different area)
# slideButton - Similar to drag button, but with a toggle setting


######## clickButton Class ###############
# Defines a simple object that represents a clickable button
# Requires a Rect indicating the target for the click, and triggerFunc to be
# called when a click occurs
##########################################

class clickButton:

	
	#Button initializer
	def __init__(self, targetRect=None, triggerFunc=None, currentValue=1):
		#the target for this button
		self.targetRect = None
		#flag indicating if this button has been pressed
		self.pressed = 0
		
		#Position that we were pressed at
		self.pressedPos = ()
		
		#flag indicating if this button has been released
		self.released = 0
		
		#Position that we were released at
		self.releasedPos = ()
		
		#Button value; is always 1 for click buttons, but useful in the future
		self.currentValue = 1
		
		#callback function to be executed when button is clicked
		self.callback = None

		##Now apply arguments to override defaults
		self.targetRect = targetRect
		self.callback = triggerFunc
		self.currentValue = currentValue
		
		#String to indicate foreign value that this should show whenever screen is redrawn or interacted with
		self.defaultValue = ""
		
		#string to indicate foreign value that this should show when the screen is first drawn/initialized
		self.initValue = ""
		
		
		#enabled property, used with enable or disable methods
		self.enabled = 1
		
		#variable to watch that determines enabled/disabled state
		self.enableCondition = ""
		self.enableConditionTarget = 1  #default; what should the enableCondition equate to?

	
	#Method to check to see if the mouse is within our rect
	def checkForHit(self):
		hit = 0
		#Quick error check to make sure a rect has been defined for us
		if (self.targetRect == None):
			return 0
		
		#Get the mouse position
		mousePos = pygame.mouse.get_pos()
		
		if (self.targetRect.collidepoint(mousePos)):
			hit = 1
		
		return hit
	
		
	#Method to handle the press event
	def handlePress(self):
		#check to see if the mouse is within our rect
		if (self.enabled == 1):
			#reset pressed to be safe
			self.pressed = self.checkForHit()
			
			if (self.pressed):
				self.pressedPos = pygame.mouse.get_pos()
			else:
				self.pressedPos = ()
		
	
	#Method to handle the release event
	def handleRelease(self):
		self.released = self.checkForHit()
		
		if (self.released):
			self.releasedPos = pygame.mouse.get_pos()
		else:
			self.releasedPos = ()
		

		if ((self.pressed == 1) and (self.released == 1) and (self.enabled == 1)):
			
			if (self.callback != None):
				self.callback(self)
		
		#turn off hit since mouse is now up
		self.pressed = 0
		self.pressedPos = ()
		
	#method to enable or disable the button
	def enable(self):
		self.enabled = 1;
		
	def disable(self):
		self.enabled = 0;
		
	def setDefault(self):
		#check to see if we should be enabled or not
		if (self.enableCondition != ""):
			
			test = eval(self.enableCondition)
			if (test == self.enableConditionTarget):
				self.enabled = 1
			else:
				self.enabled = 0

		if ((self.defaultValue != "") and (self.defaultValue != "0")):
			self.currentValue = int(eval(self.defaultValue))
	
	#Method to set an enable/disable condition
	def setEnableCondition(self, conditionStr, targetVal=1):
		self.enableCondition = conditionStr
		self.enableConditionTarget = targetVal
		
	#Method to set a foreign initial value
	def setInitValue(self, initValStr=""):
		self.initValue = initValStr
		
		
	def handleInit(self, screenBuff):
		if (self.initValue != ""):
			self.currentValue = int(eval(self.initValue))
		


######## Done clickButton Class ###############

######## dragButton Class #####################
# Extends/updates the clickButton class to give it actions based
# on "drag gestures" instead of just clicks
#
# Create a new instance just like with clickButton, then
# call the "addDragCallback" to add drag calls
#     takes args: direction - "left", "right", "up", or "down" to indicate direction of drag
#                 offset - takes an absolute value indicating the offset required
#                 callbackFunc - the function to be called when the drag finishes
###############################################

class dragButton(clickButton):
	
	def __init__(self, targetRect=None, triggerFunc=None, currentValue=1):
	
		clickButton.__init__(self, targetRect, triggerFunc, currentValue)
	
		#property to store the drag callbacks
		self.dragCallbacks = {}
		self.dragCallbacks["up"] = None
		self.dragCallbacks["down"] = None
		self.dragCallbacks["left"] = None
		self.dragCallbacks["right"] = None
		
		#property to store the drag offsets
		self.dragOffsets = {}
		self.dragOffsets["up"] = 0
		self.dragOffsets["down"] = 0
		self.dragOffsets["left"] = 0
		self.dragOffsets["right"] = 0

	#Method to add a drag callback
	def addDragCallback(self, direction, offset, callbackFunc):
		self.dragCallbacks[direction] = callbackFunc
		self.dragOffsets[direction] = offset

	#Override the default method for the release
	def handleRelease(self):
		self.released = self.checkForHit()
		self.releasedPos = pygame.mouse.get_pos()

		#Track as we only want the regular click action to happen if a drag action doesn't...or it'll be confusing
		#for the user...
		doneDrag = 0
		if ((self.pressed == 1)):
			doneDrag = self.checkForDrag()
		
		#do drag fired, so check for a regular click action
		if ((self.pressed == 1) and (self.released == 1) and (doneDrag == 0) and (self.enabled == 1)):
			if (self.callback != None):
				self.callback(self)
			
		
		#turn off hit since mouse is now up
		self.pressed = 0
		self.pressedPos = ()
		
	#Method to check for drag events and fire callback accordingly
	def checkForDrag(self):

		doneDrag = 0
		if (self.enabled == 1):
		#check for up drag
			if ((self.dragCallbacks["up"] != None) and (self.dragOffsets["up"] > 0) ):
				yDelta = self.releasedPos[1] - self.pressedPos[1]
				if (yDelta >= self.dragOffsets["up"]):
					
					#Execute the callback
					self.dragCallbacks["up"](self)
					doneDrag = 1
			#check for down drag
			if ((self.dragCallbacks["down"] != None) and (self.dragOffsets["down"] > 0) ):
				yDelta = self.pressedPos[1] - self.releasedPos[1]
	
				if (yDelta >= self.dragOffsets["up"]):
					#Execute the callback
					self.dragCallbacks["down"](self)
					doneDrag = 1
			#check for left drag
			if ((self.dragCallbacks["left"] != None) and (self.dragOffsets["left"] > 0) ):
				xDelta = self.releasedPos[0] - self.pressedPos[0]
				if (xDelta >= self.dragOffsets["left"]):
					#Execute the callback
					self.dragCallbacks["left"](self)
					doneDrag = 1		
			#check for right drag
			if ((self.dragCallbacks["right"] != None) and (self.dragOffsets["right"] > 0) ):
				xDelta = self.pressedPos[0] - self.releasedPos[0]
				if (xDelta >= self.dragOffsets["left"]):
					#Execute the callback
					self.dragCallbacks["right"](self)
					doneDrag = 1
		
		return doneDrag		
######## Done dragButton Class #####################

######## digitScroller Class #############################
# Extends the dragButton class to create a digit scroller
# as used on the alarm controller page
#
# Accepts additional arguments:
#              - range : list identifying [min, max] values... 0-9 by default
#
##########################################################

class digitScroller(dragButton):

	def __init__(self, targetRect=None, triggerFunc=None, currentValue=1, range=[0,9]):
		#Initialize the underlying dragButton
		dragButton.__init__(self, targetRect, None, currentValue)
		
		self.changeValCallback = None
		#Define a changeVal callback
		if (triggerFunc != None):
			self.changeValCallback = triggerFunc
		
		self.range = range
		
		self.imageRect = Rect(targetRect.left, targetRect.top + 20,  targetRect.width, targetRect.height)
		
		#Setup the callback handlers
		self.addDragCallback("up", 5, self.scrollUp)
		self.addDragCallback("down", 5, self.scrollDown)
		
		#Create the sub-buttons for the static up/down (incase you don't want the gestures)
		self.subUp = clickButton(Rect(targetRect.left, targetRect.top, targetRect.width, 30), self.scrollUp)
		
		self.subDown = clickButton(Rect(targetRect.left, targetRect.top + targetRect.height + 20, targetRect.width, 30), self.scrollDown)
		
		#set the initial value
		self.setValue(currentValue, 1)
		
	
	#Pass messages from mouse events along to subButtons as well
	def handlePress(self):
		dragButton.handlePress(self)
		self.subUp.handlePress()
		self.subDown.handlePress()
		
	def handleRelease(self):
		dragButton.handleRelease(self)
		self.subUp.handleRelease()
		self.subDown.handleRelease()
	
	def scrollUp(self, button):
		
		#Scroll this digit up one
		if (self.currentValue < self.range[1]):
			#Still allowed to scroll up

			#Play the release sound...?... sure, why not...
			soundrelease()
			
			self.setValue(self.currentValue + 1)

	
	def scrollDown(self, button):
		#Scroll down one digit
		if (self.currentValue > self.range[0]):
			#Still allowed to scroll down
			
			#Play the release sound...?... sure, why not...
			soundrelease()
			
			self.setValue(self.currentValue -1)
			
				
	def setValue(self, newValue, fromInit = 0, tempBuffer=None):
		#External method to specifically set the value of this scroller
		if (self.range[0] <= newValue <= self.range[1]):
			self.currentValue = newValue
		elif (newValue > self.range[1]):
			self.currentValue = self.range[1]
		elif (newValue < self.range[0]):
			self.currentValue = self.range[0]
		
		if (fromInit != 1):
			#draw the new digit
			self.drawButton(tempBuffer)
				
			if (self.changeValCallback != None):
				self.changeValCallback(self)
			
			
	def setRange(self, newRange, fromInit = 0):
		self.range = newRange
		if (self.currentValue > self.range[1]):
			self.setValue(self.range[1], fromInit)
		elif (self.currentValue < self.range[0]):
			self.setValue(self.range[0], fromInit)
					
					
	#Method to draw the scrolling Digit
	def drawButton(self, tempBuffer = None):
		#print "Drawing digit"
		if (tempBuffer == None):
			#Get a reference to the surface
			myScreen = pygame.display.get_surface()
		else:
			myScreen = tempBuffer
		
		
		#Redraw the digit
		myScreen.blit(ci.al_numeri[self.currentValue], self.imageRect)
	
		if (tempBuffer == None):
			
			#Refresh the redrawn part of the screen
			pygame.display.update(self.imageRect)
	
	def handleInit(self, tempBuffer=None):
		
		if (self.initValue != ""):
			self.setValue(int(eval(self.initValue)), 0, tempBuffer)


######## doubleHoursScroller Class #########
#
#  Simple wrapper class that creates two digitScrollers and sets them
# up with some restrictions so that it's impossible to select invalid times
#
#  Takes the arguments - digit1Rect : Rect of first digit Scroller
#                      - digit2Rect : Rect of second digit Scroller
#					   - militaryTime :1 for 24 hour, 0 for 12 hour operations
#
# needs some more work..... obviously....
#
###########################################

class doubleHoursScroller:

	def __init__(self, digit1Rect, digit2Rect, militaryTimePointer=""):
	
		self.firstDigit = None
		self.secondDigit = None
	
		if (militaryTimePointer == ""):
			self.militaryTime = 0
			self.militaryTimePointer = ""
		else:
			self.militaryTimePointer = militaryTimePointer
			self.militaryTime = eval(self.militaryTimePointer)
	
		if (self.militaryTime):
			self.digit1Range = [0, 2]
			self.digit2Range = [0, 9]
		else:
			self.digit1Range = [0, 1]
			self.digit2Range = [0, 9]
		
		self.secondDigit = digitScroller(digit2Rect, None, 0, self.digit2Range)
		self.firstDigit = digitScroller(digit1Rect, self.checkDigit1, 0, self.digit1Range)
		
		self.checkDigit1(self, 1)
	
	#Method to track digit one and limit it accordingly
	def checkDigit1(self, buttonRef, fromInit = 0):
		
		if (self.militaryTimePointer != ""):
			self.militaryTime = eval(self.militaryTimePointer)
	
		try:
			if (self.militaryTime == 1):
				
				#In 24 hour mode, range can be 00 - 23, so set accordingly
				self.firstDigit.setRange([0, 2], fromInit)
				if (self.firstDigit.currentValue == 0):
					self.secondDigit.setRange([0,9], fromInit)
				elif (self.firstDigit.currentValue == 1):
					self.secondDigit.setRange([0,9], fromInit)
				else:
					self.secondDigit.setRange([0, 3], fromInit)
			else:
				self.firstDigit.setRange([0, 1], fromInit)
				#In 12 hour mode, range can only be 01-12
				if (self.firstDigit.currentValue == 0):
					self.secondDigit.setRange([1, 9], fromInit)
				else:
					self.secondDigit.setRange([0, 2], fromInit)
		except:
			pass
	
	#Pass mouse events along
	#Pass messages from mouse events along to subButtons as well
	def handlePress(self):
		self.firstDigit.handlePress()
		self.secondDigit.handlePress()
		
	def handleRelease(self):
		self.firstDigit.handleRelease()
		self.secondDigit.handleRelease()
	
	def setDefault(self):
		#This is needed but I'm not quite sure when/why yet... maybe it's not... but I have a feeling...
		self.checkDigit1(self)
		
		if ((self.firstDigit.defaultValue != "") and (self.firstDigit.defaultValue != "0")):
			self.firstDigit.setValue(int(eval(self.firstDigit.defaultValue)))
		
		if ((self.secondDigit.defaultValue != "") and (self.secondDigit.defaultValue != "0")):
			self.secondDigit.setValue(int(eval(self.secondDigit.defaultValue)))
		
		
	def drawButton(self, tempBuffer = None):
		self.firstDigit.drawButton(tempBuffer)
		self.secondDigit.drawButton(tempBuffer)
	
	#Set the values to be re-read any time the init method is called...
	def setInitValues(self, defaultVal1Str="", defaultVal2Str=""):
		self.firstDigit.setInitValue(defaultVal1Str)
		self.secondDigit.setInitValue(defaultVal2Str)
		
	def handleInit(self, tempBuffer=None):
		self.firstDigit.handleInit(tempBuffer)
		self.secondDigit.handleInit(tempBuffer)


######## slideButton Class ###############
# Extends the clickButton class to turn it into a sliding 
# button instead of a clickable one
#
# NOTE!! The currentValue argument should be a string, not an int! That way you
# can leave it pointed at a global var, config object, etc and it will
# still work properly...
##########################################

class slideButton(clickButton):
	
	#Extended creator
	def __init__(self, targetRect=None, triggerFunc=None, currentValue="", slideImgObj=None, slideMaskObj=None, maxPos=70, minPos=-70):
		clickButton.__init__(self, targetRect, None)
		
		#Additional properties
		self.slideImgObj = None        #Image object to be displayed
		self.slideMaskObj = None       #Mask to overlay image
		
		#Screen surface element
		self.myScreen = None
		
		#callback to override clickButton one... this is necessary, just trust me here
		self.dragCallback = None
		
		#max and min positions for slider image (max pos is on, minpos is off)
		self.maxPos = 70
		self.minPos = -70
		
		self.defaultValue = "0"
		
		
		self.slideImgObj = slideImgObj 
		self.myScreen = pygame.display.get_surface()
		self.slideMaskObj = slideMaskObj
		self.dragCallback = triggerFunc
		self.maxPos = maxPos
		self.minPos = minPos
		
		if (currentValue != ""):
			self.defaultValue = currentValue

	
	#Method to handle the dragging of a slide switch
	def handleDrag(self):

		if ((self.pressed) and (self.enabled == 1)):
			#Mouse was pressed on us, so drag is valid

			
			#get the current mouse position
			mouseX, mouseY = pygame.mouse.get_pos()
			offset = mouseX - self.pressedPos[0]
			

			
			#Current value is zero, then calculate based on that position
			if (self.currentValue == 0):
				if (offset < 0):
					offset = 0
				if (offset > self.maxPos):
					offset = self.maxPos
					
				
				self.myScreen.blit(self.slideImgObj, (self.targetRect.left - self.maxPos - 6 + offset, self.targetRect.top + 1))
			elif (self.currentValue == 1):
				if (offset > 0):
					offset = 0
				if (offset < self.minPos):
					offset = self.minPos
				self.myScreen.blit(self.slideImgObj, (self.targetRect.left - 6 + offset, self.targetRect.top + 1))

			#Now draw the mask ontop of the image
			if (self.slideMaskObj != None):
				self.myScreen.blit(self.slideMaskObj, (self.targetRect.left, self.targetRect.top))
				
			#Finally, update only the part of the screen that we've affected
			pygame.display.update(self.targetRect)
			
	#Method to extend the release to make our slider "snap" to the closest value
	def handleRelease(self):
		self.released = self.checkForHit()
		
		self.releasedPos = pygame.mouse.get_pos()
		
		#now the extended stuff
		if ((self.pressed == 1) and (self.enabled == 1)):
			#check to see which side we're closer to, and force to that end
			offset = self.releasedPos[0] - self.pressedPos[0] 
			if (offset > 35):
				self.currentValue = 1
			elif (offset < -35):
				self.currentValue = 0
			#draw the snap movement
			
			self.drawButton()
			
			if (self.dragCallback != None):
				self.dragCallback(self)
				
		#turn off hit since mouse is now up
		self.pressed = 0
		self.pressedPos = ()
		
		
	#Method to draw the switch based on the value
	def drawButton(self, tempBuffer = None):
		if (self.enabled == 1):
			if (tempBuffer == None):
				thisBuff = self.myScreen
			else:
				thisBuff = tempBuffer
			#Make sure we only redraw the rect we want
			thisBuff.set_clip(self.targetRect)
		
			if (self.currentValue == 1):
				thisBuff.blit(self.slideImgObj,(self.targetRect.left - 6,self.targetRect.top+1))
			
			else:
				thisBuff.blit(self.slideImgObj,(self.targetRect.left - self.maxPos - 6,self.targetRect.top+1))
					
			#Now draw the mask ontop of the image
			if (self.slideMaskObj != None):
				thisBuff.blit(self.slideMaskObj, (self.targetRect.left, self.targetRect.top))
			
			#only redraw locally if not using a buffer screen surface		
			if (tempBuffer == None):
				#Finally, update only the part of the screen that we've affected
				pygame.display.update(self.targetRect)
			
			#Okay, done, so make sure the whole screen can be redrawn
			thisBuff.set_clip(ci.screenSize)
######## Done slideButton Class ###############	



######################## Sound Handlers (Play sound when a button gets clicked) ##############
def soundtap():
	if ci.tablet==1:
		ci.hildon.hildon_play_system_sound(ci.path+"ui-key_press.wav")
	
def soundrelease():
	if ci.tablet==1:
		ci.hildon.hildon_play_system_sound(ci.path+"ui-pen_down.wav")


################### DONE BUTTON DEFITINITIONS #################################

