#####################################################################
# G-Streamer control/playback Object
#
# By Rob Williams (jolouis) for the FlipClock project
# Provides a simple GStreamer interface for playing back mp3s/audio
# using the native gstreamer app.
# 
# loosely based on post on Nokia Maemo forums:
# http://wiki.forum.nokia.com/index.php/How_to_create_a_mp3_player_in_maemo
######################################################################

#Import python g-streamer bindings
import pygst

pygst.require("0.10") #uhh sure, why not...

#import gStreamer itself
import gst

#gobject, for setting up timeouts, etc
import gobject


class mediaPlayer:

	### Method to initialize the gstreamer instance
	def __init__(self, outputModule="mp3"):
		self.status = self.setupPipe(outputModule)
	
	
	def setupPipe(self, outputModule):
		#Create the pipeline according to the mode
		pipestr = ""
		if (outputModule == "mp3"):
			pipestr = 'gnomevfssrc name="source" ! dspmp3sink name="sink"'
		elif(outputModule == "wav"):
			pipestr = 'gnomevfssrc name="source" ! wavparse ! dsppcmsink name="sink"'
	
		if (pipestr == ""):
			#not supported type, so abort
			return 0
	
		#Now create the pipe from the string
		try:
			self.playerPipe = gst.parse_launch(pipestr)       
		except gobject.GError, e:
			print "could not create pipeline, " +str(e)
			return 0
	
		self.audioSrc = self.playerPipe.get_by_name("source")
		self.audioSink = self.playerPipe.get_by_name("sink")
	
	
	
	
	
		#Create the pipeline to gstreamer
		#self.playerPipe = gst.Pipeline("flipPipe")
	
		#create the input source and add it to the pipe
		#(Input is any file://, http://, etc... as noted here:
		#http://gstreamer.freedesktop.org/data/doc/gstreamer/head/gst-plugins-base-plugins/html/gst-plugins-base-plugins-gnomevfssrc.html#GstGnomeVFSSrc--location
		#self.audioSrc = gst.element_factory_make("gnomevfssrc", "source")
		#self.playerPipe.add(self.audioSrc)
		
		#try:
		#Create the output source and add to the pipe
		# (MP3 using DSP)
		#self.audioSink = gst.element_factory_make(outputModule, "sink")
		#self.playerPipe.add(self.audioSink)
		
		#Link the source to the destination
		#self.audioSrc.link(self.audioSink)
		#except:
		#print "output module " + outputModule + " failed!"
			
	
	### Method to load an mp3
	def loadFile(self, theFile):
		#stop player if currently playing to be safe
		if (self.playerPipe.get_state() == gst.STATE_PLAYING):
			self.stopAudio()

		#Make sure the file has a prefix
		hasPre = 0
		for pre in ["file://", "http://"]:
			if (theFile.lower().startswith(pre)):
				hasPre = 1
				break
		
		if (hasPre == 0):
			theFile = "file://" + theFile
		#Set the source file
		self.audioSrc.set_property("location", theFile)
		#self.playerPipe.set_state(gst.STATE_READY) 
	
	### Method to start playing
	def playAudio(self):
		self.playerPipe.set_state(gst.STATE_READY) 
		test = self.playerPipe.set_state(gst.STATE_PLAYING)
		
	### Method to stop playing
	def stopAudio(self):
		if self.playerPipe.get_state() != gst.STATE_PAUSED:
			self.playerPipe.set_state(gst.STATE_PAUSED)
		if self.playerPipe.get_state() != gst.STATE_NULL:
			self.playerPipe.set_state(gst.STATE_NULL)
	
	##Method to determine if playing or not
	def getStatus(self):
		rawState = self.playerPipe.get_state()
		print rawState[1]
		realState = "None"
		if (rawState[1] == gst.STATE_PLAYING):
			realState = "Playing"
		elif (rawState[1] == gst.STATE_PAUSED):
			realState = "Paused"
		print realState
		return realState
		
	
	### Method to set the volume of the sink
	## Volume is passed in as an int between 0 and 100
	def setVolume(self, volLevel):
		if (0 <= volLevel <= 100):
			realVol = int(round((65535.0 / 100.0) * volLevel))
			self.audioSink.set_property("volume", realVol)

	## Method to return the volume of the sink
	# as an in between 0 and 100
	def getVolume(self):
		rawVol = self.audioSink.get_property("volume")
		realVol = int(round((float(rawVol) / 65535.0) * 100))
		return realVol
		
			
			 
########## Done class defintion ################



########## Media Controller #####################
class mediaControllerClass:
	def __init__(self):
		self.fileType = "mp3"
		self.currentFile = ""
		
		self.mp3Player = mediaPlayer("mp3")
		#self.wavPlayer = mediaPlayer("wav")

		self.mp3Player.playerPipe.get_bus().add_watch(self.watchStatus)
		#self.wavPlayer.playerPipe.get_bus().add_watch(self.watchStatus)

		#default to MP3 Player
		self.currentPlayer = self.mp3Player
		
		#callback for when the stream is done
		self.doneCallback = None
		
		#Loop mode, 1 for looping, 0 for play and move on
		self.loopPlay = 0

	##General command to load an audio file and prep for playback
	def loadFile(self, fileToPlay):
		if (fileToPlay.lower().endswith("mp3")):
			#File is MP3
			self.currentPlayer = self.mp3Player
			self.fileType = "mp3"
		#else:
		#	#Assume file can be handled by generic PCM output
		#	self.currentPlayer = mediaPlayer("wav")
		#	self.fileType = "wav"

		self.currentFile = fileToPlay
		self.currentPlayer.loadFile(fileToPlay)

	## General play command
	def play(self):
		self.currentPlayer.playAudio()

	## General stop command
	def stop(self):
		self.loopPlay = 0
		self.currentPlayer.stopAudio()
		
	## time-based fade in play
	def fadeSoundIn(self, time=20000, maxVol=80):
		#Start by setting sound to 0 volume
		self.currentPlayer.setVolume(20)
		
		print "set vol to 0"
		#start playing
		self.currentPlayer.playAudio()
		#Sound will go in 5 volume steps, so
		self.stepTime = time / 5
		
		#set timeout
		gobject.timeout_add(self.stepTime, self.stepVolumeUp)
		
	## Helper function for fading volume up
	def stepVolumeUp(self):
		currVol = self.currentPlayer.getVolume();

		if currVol < 100:
			self.currentPlayer.setVolume(currVol + 20);
			
			state = self.currentPlayer.getStatus()
			if (state == "Playing"):
				#set timeout
				gobject.timeout_add(self.stepTime, self.stepVolumeUp)
			
	## Method to control looping/playback state
	def watchStatus(self, bus, msg):
		#Get the type of message sent to us
		type = msg.type

		if (type == gst.MESSAGE_EOS):
			#Stream is done playing
			if (self.loopPlay == 1):
				print "looping"
				
				#We want to loop, so just start the stream again
				self.currentPlayer.playAudio()
			else:
				print "done playing"
				self.currentPlayer.stopAudio()
				#We don't want to loop, so call the "done playing" callback
				if (self.doneCallback != None):
					self.doneCallback(self)
		return True
				


	########## Getter/Setters ###########
	def setCallback(self, callback):
		##Assign a callback function to be executed when the stream finishes (non-looping mode)
		self.doneCallback = callback
		
	def setLoopMode(self, mode):
		##should the player loop the file or just play and stop
		self.loopPlay = mode




mediaController = mediaControllerClass()		
	



