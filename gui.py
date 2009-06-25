#
#Copyright (C) 2009  asylumfunk
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You may obtain a copy of this license at:
#  http://www.gnu.org/licenses/gpl-3.0.html

"""Presentation layer"""

#Standard modules
import sys
#Third-party modules
import twitter
import xbmc
import xbmcgui
#Project modules
import act
import config
import lang

class gui:
	"""Handles the scripts user interface"""

	"""
	Description:
		Default constructor
		Initializes the UI language
		Loads the user's credentials, if they are saved
	"""
	def __init__( self ):
		self.lang = lang.lang()
		credentials = config.loadCredentials()
		self.username = credentials[ 0 ]
		self.password = credentials[ 1 ]
		self.api = twitter.Api( username = self.username, password = self.password )
		self.player = player = xbmc.Player()
		self.menuOptions = [
			self.lang.get( "MainMenu_Options_UpdateManually" )
			, self.lang.get( "MainMenu_Options_EditAccount" )
			, self.lang.get( "MainMenu_Options_About" )
			, self.lang.get( "MainMenu_Options_Exit" )
		]
		self.version = sys.modules[ "__main__" ].__version__

	"""
	Description:
		Displays the "About" dialog
	"""
	def about( self ):
		dialog = xbmcgui.Dialog()
		dialog.ok( config.About_TagLine, sys.modules[ "__main__" ].__author__, config.About_Url, config.About_Email )

	"""
	Description:
		Displays the script's main menu
		Serves as the driver
	"""
	def displayMainMenu( self ):
		menu = xbmcgui.Dialog()
		choice = 0
		audioIsPlaying = False
		videoIsPlaying = False
		mediaIsPlaying = False
		while choice >= 0:
			options = self.menuOptions
			audioIsPlaying = self.player.isPlayingAudio()
			videoIsPlaying = self.player.isPlayingVideo()
			mediaIsPlaying = audioIsPlaying or videoIsPlaying
			if audioIsPlaying:
				options.insert( 0, self.lang.get( "MainMenu_Options_UpdateWithAudio" ) )
			elif videoIsPlaying:
				options.insert( 0, self.lang.get( "MainMenu_Options_UpdateWithVideo" ) )
			choice = menu.select( self.lang.get( "ApplicationName" ) + ", v" + self.version, options )
			print str(choice)
			if mediaIsPlaying:
				options.pop( 0 )
			elif choice < 0:
				break
			else:
				choice = choice + 1
			if choice == 0:
				self.tweetWhatImDoing()
			elif choice == 1:
				self.tweetManually()
			elif choice == 2:
				self.editCredentials()
			elif choice == 3:
				self.about()
			else:
				break

	"""
	Description:
		Prompts the user for their authentication credentials
		If the user enters both username and password, the information is saved.
	"""
	def editCredentials( self ):
		username = self.username
		password = self.password
		while True:
			username = self.editUsername( username )
			if username is None:
				return
			password = self.editPassword()
			if password is not None:
				break
		self.setCredentials( username, password )

	"""
	Description:
		Prompts the user for their password
	Returns:
		Accept: the user-supplied input
		Cancel: None
	"""
	def editPassword( self ):
		keyboard = xbmc.Keyboard( "", self.lang.get( "EnterPassword" ), True )
		keyboard.doModal()
		if keyboard.isConfirmed():
			password = keyboard.getText().strip()
			if password != "":
				return password
		return None

	"""
	Description:
		Prompts the user for their username
	Returns:
		Accept: the user-supplied input
		Cancel: None
	"""
	def editUsername( self, username = None ):
		if username is None:
			username = ""
		keyboard = xbmc.Keyboard( username, self.lang.get( "EnterUsername" ) )
		keyboard.doModal()
		if keyboard.isConfirmed():
			username = keyboard.getText().strip()
			if username != "":
				return username
		return None

	"""
	Description:
		Updates & saves the user's credentials
	"""
	def setCredentials( self, username, password ):
		self.username = username
		self.password = password
		self.api.SetCredentials( username, password )
		config.saveCredentials( username, password )

	"""
	Description:
		On the first run, user is prompted for their credentials
		Displays the main menu
	"""
	def start( self ):
		if self.username is None:
			self.editCredentials()
			if self.username is None:
				print "You must log in."
				return
		self.displayMainMenu()

	"""
	Description:
		Updates the status for the currently authenticated user
	Args:
		message::string : the message to be sent
	Returns:
		True
	TODO:
		actually check if the status was successfully updated
	"""
	def tweet( self, message ):
		try:
			self.api.PostUpdate( message )
			self.alertStatusSuccessfullyUpdated()
			return True
		except:
			self.alertStatusNotUpdated()
			return False
		#todo: actually confirm

	"""
	Description:
		Prompts the user to enter a status update
		Alerts user and continues to prompt if status is either too long or empty
	Returns:
		Accept: Boolean result flag
		Cancel: False
	"""
	def tweetManually( self ):
		keyboard = xbmc.Keyboard( "", self.lang.get( "Tweet_EnterStatus" ) )
		while True:
			keyboard.doModal()
			if keyboard.isConfirmed():
				message = keyboard.getText().strip()
				if message == "":
					self.alertStatusEmpty()
				elif len( message ) > twitter.CHARACTER_LIMIT:
					self.alertStatusTooLong
				else:
					return self.tweet( message )
			else:
				return False

	"""
	Description:
		Automatically updates the user's status with the video/music they're currently playing
		Silently returns if user isn't playing any media
	Returns:
		Boolean result flag
	TODO:
		disable this option if user isn't playing any media
	"""
	def tweetWhatImDoing( self ):
		if self.player.isPlayingAudio():
			return self.tweetWhatImListeningTo()
		elif self.player.isPlayingVideo():
			return self.tweetWhatImWatching()
		else:
			return False

	"""
	Description:
		Updates the user's status with the music they're currently listening to
	Returns:
		Boolean result flag
	"""
	def tweetWhatImListeningTo( self ):
		try:
			song = self.player.getMusicInfoTag()
		except:
			return False
		info = self.lang.get( "TweetMusic_MessageFormat" ).replace( "{0}", song.getArtist() ).replace( "{1}", song.getTitle() )
		message = act.appendFooterToStatus( info, twitter.CHARACTER_LIMIT )
		return self.tweet( message )

	"""
	Description:
		Updates the user's status with the video they're currently watching
	Returns:
		Boolean result flag
	"""
	def tweetWhatImWatching( self ):
		try:
			video = self.player.getVideoInfoTag()
		except:
			return False
		title = video.getTitle()
		if title == "":
			title = act.parseTitleFromFilename( self.player.getPlayingFile() )
		info = self.lang.get( "TweetVideo_MessageFormat" ).encode( "utf_8" ).replace( "{0}", title )
		message = act.appendFooterToStatus( info, twitter.CHARACTER_LIMIT )
		return self.tweet( message )

	"""
	Description:
		Alerts the user that their status cannot be empty
	"""
	def alertStatusEmpty( self ):
		dialog = xbmcgui.Dialog()
		dialog.ok( self.lang.get( "Tweet_Alert_Empty_Title" ), self.lang.get( "Tweet_Alert_Empty_Text" ) )

	"""
	Description:
		Alerts the user that their status cannot exceed the maximum length
	"""
	def alertStatusTooLong( self ):
		dialog = xbmcgui.Dialog()
		dialog.ok( self.lang.get( "Tweet_Alert_TooLong_Title" ), self.lang.get( "Tweet_Alert_TooLong_Text" ).replace( "{0}", str( twitter.CHARACTER_LIMIT ) ) )

	"""
	Description:
		Alerts the user that their status could not be updated
	"""
	def alertStatusNotUpdated( self ):
		dialog = xbmcgui.Dialog()
		dialog.ok( self.lang.get( "Tweet_Alert_StatusNotUpdated_Title" ), self.lang.get( "Tweet_Alert_StatusNotUpdated_Text1" ), self.lang.get( "Tweet_Alert_StatusNotUpdated_Text2" ), self.lang.get( "Tweet_Alert_StatusNotUpdated_Text3" ) )

	"""
	Description:
		Alerts the user that their status was successfully updated
	"""
	def alertStatusSuccessfullyUpdated( self ):
		dialog = xbmcgui.Dialog()
		dialog.ok( self.lang.get( "Tweet_Alert_Success_Title" ), self.lang.get( "Tweet_Alert_Success_Text" ) )