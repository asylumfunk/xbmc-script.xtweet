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
import time
import urllib2
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
		self.api.SetSource( self.lang.get( "ApplicationName" ) )
		self.player = player = xbmc.Player()
		self.menuOptions_Main = [
			self.lang.get( "MainMenu_Options_UpdateManually" )
			, self.lang.get( "MainMenu_Options_ViewFriendsTimeline" )
			, self.lang.get( "MainMenu_Options_Following" )
			, self.lang.get( "MainMenu_Options_Followers" )
			, self.lang.get( "MainMenu_Options_DirectMessages" )
			, self.lang.get( "MainMenu_Options_EditAccount" )
			, self.lang.get( "MainMenu_Options_About" )
			, self.lang.get( "MainMenu_Options_Exit" )
		]
		self.menuOptions_DirectMessages = [
			self.lang.get( "Menu_DirectMessages_Compose" )
			, self.lang.get( "Menu_DirectMessages_Inbox" )
			, self.lang.get( "Menu_DirectMessages_Sent" )
		]
		self.DirectMessageType = {
			"sent" : 1,
			"received" : 2
		}
		self.UsersListType = {
			"following" : 1,
			"followers" : 2
		}
		self.version = sys.modules[ "__main__" ].__version__
		self.ApplicationNameWithVersion = self.lang.get( "ApplicationName" ) + ", v" + self.version

	"""
	Description:
		Displays the "About" dialog
	"""
	def about( self ):
		dialog = xbmcgui.Dialog()
		dialog.ok( config.About_TagLine, sys.modules[ "__main__" ].__author__, config.About_Url, config.About_Email )

	"""
	Description:
		Alerts the user that the Direct Message has been deleted
	"""
	def alertDirectMessageDeleted( self ):
		dialog = xbmcgui.Dialog()
		return dialog.ok( self.lang.get( "Success" ), self.lang.get( "Message_Alert_DirectMessage_Deleted" ) )

	"""
	Description:
		Alerts the user that their message cannot be empty
	"""
	def alertMessageEmpty( self ):
		dialog = xbmcgui.Dialog()
		return dialog.ok( self.lang.get( "Warning" ), self.lang.get( "Message_Alert_Empty_Text" ) )

	"""
	Description:
		Alerts the user that their message could not be sent
	"""
	def alertMessageNotSent( self ):
		dialog = xbmcgui.Dialog()
		return dialog.ok( self.lang.get( "Warning" ), self.lang.get( "Message_Alert_NotSent1" ), self.lang.get( "Message_Alert_NotSent2" ), self.lang.get( "Message_Alert_NotSent3" ) )

	"""
	Description:
		Alerts the user that their message was successfully sent
	"""
	def alertMessageSuccessfullySent( self ):
		dialog = xbmcgui.Dialog()
		return dialog.ok( self.lang.get( "Success" ), self.lang.get( "Message_Alert_SentSuccessfully" ) )

	"""
	Description:
		Alerts the user that their message cannot exceed the maximum length
	"""
	def alertMessageTooLong( self ):
		dialog = xbmcgui.Dialog()
		return dialog.ok( self.lang.get( "Warning" ), self.lang.get( "Message_Alert_TooLong_Text" ) %
																							{ "maxLength" : twitter.CHARACTER_LIMIT } )

	"""
	Description:
		Alerts the user that their status cannot be empty
	"""
	def alertStatusEmpty( self ):
		dialog = xbmcgui.Dialog()
		dialog.ok( self.lang.get( "Warning" ), self.lang.get( "Tweet_Alert_Empty_Text" ) )

	"""
	Description:
		Alerts the user that their status could not be updated
	"""
	def alertStatusNotUpdated( self ):
		dialog = xbmcgui.Dialog()
		dialog.ok( self.lang.get( "Warning" ), self.lang.get( "Tweet_Alert_StatusNotUpdated_Text1" ), self.lang.get( "Tweet_Alert_StatusNotUpdated_Text2" ), self.lang.get( "Tweet_Alert_StatusNotUpdated_Text3" ) )

	"""
	Description:
		Alerts the user that their status was successfully updated
	"""
	def alertStatusSuccessfullyUpdated( self ):
		dialog = xbmcgui.Dialog()
		dialog.ok( self.lang.get( "Success" ), self.lang.get( "Tweet_Alert_Success_Text" ) )

	"""
	Description:
		Alerts the user that their status cannot exceed the maximum length
	"""
	def alertStatusTooLong( self ):
		dialog = xbmcgui.Dialog()
		dialog.ok( self.lang.get( "Warning" ), self.lang.get( "Tweet_Alert_TooLong_Text" ) %
																				{ "maxLength" : twitter.CHARACTER_LIMIT } )

	"""
	Description:
		Alerts the user that the requested user timeline is protected
	"""
	def alertTimelineProtected( self, user ):
		dialog = xbmcgui.Dialog()
		dialog.ok( self.lang.get( "UserTimeline_Protected_Header_Format" ) % { 'userName' : user.GetScreenName() },
					self.lang.get( "UserTimeline_Protected_Line1" ),
					self.lang.get( "UserTimeline_Protected_Line2" ) )

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
		Formats the display string for a direct message
	Args:
		message::twitter.DirectMessage - the message to be displayed
		messageType::self.DirectMessageType - "sent" or "received"
	Returns:
		string - the properly formatted direct message string
	"""
	def formatDirectMessageDisplay( self, message, messageType ):
		if messageType == self.DirectMessageType[ 'sent' ]:
			userName = message.GetRecipientScreenName()
			format = self.lang.get( "DirectMessageDisplayFormat_Sent" )
		else:
			userName = message.GetSenderScreenName()
			format = self.lang.get( "DirectMessageDisplayFormat_Received" )
		text = act.stripNewlines( message.GetText() )
		created = time.localtime( message.GetCreatedAtInSeconds() )
		timestamp = time.strftime( self.lang.get( "TimestampFormat" ), created )
		return format % locals()

	"""
	Description:
		Prompts the user to update their status, mentioning a specified user
	Args:
		user::twitter.User - the user being mentioned
	Returns:
		Accept:	boolean result flag
		Cancel: None
	"""
	def mention( self, user ):
		userName = user.GetScreenName()
		message = self.promptMessage( self.lang.get( "Tweet_EnterStatus" ), self.lang.get( "Mention_Format" ) % locals() )
		if message is None:
			return None
		else:
			return self.tweet( message )

	"""
		Description:
			Confirms if the user wants to delete the message.
			If yes, the message is deleted.
		Args:
			message:twitter.DirectMessage - the message pending deletion
		Returns:
			Yes - True
			No - False
	"""
	def promptDeleteMessage( self, message ):
		dialog = xbmcgui.Dialog()
		sure = dialog.yesno( self.lang.get( "DirectMessage_DeletePrompt_Header" ),
								self.lang.get( "DirectMessage_DeletePrompt_Line1" ),
								self.lang.get( "DirectMessage_DeletePrompt_Line2" ) )
		if sure:
			self.api.DestroyDirectMessage( message.GetId() )
			self.alertDirectMessageDeleted()
		return sure

	"""
	Description:
		Prompts the user to enter a screen name
	Args:
		title::string (optional) - title prompt to be displayed
		default::string (optional) - default text to be pre-entered
		acceptEmpty::bool (optional) - whether or not the prompt should loop if the user enters an empty entry
	Returns:
		Accept: the user's input (stripped of surrounding whitespace)
		Cancel: None
	"""
	def promptScreenName( self, title = "", default = "", acceptEmpty = False ):
		keyboard = xbmc.Keyboard( default, title )
		while True:
			keyboard.doModal()
			if keyboard.isConfirmed():
				name = keyboard.getText().strip()
				if name != "" or acceptEmpty:
					return name
			else:
				return None

	"""
	Description:
		Prompts the user to enter a message
		Alerts and loops if the message is too long
	Args:
		title::string (optional) - title prompt to be displayed
		default::string (optional) - default text to be pre-entered
		acceptEmpty::bool (optional) - whether or not the prompt should loop if the user enters an empty entry
	Returns:
		Accept: the user's input (stripped of surrounding whitespace)
		Cancel: None
	"""
	def promptMessage( self, title = "", default = "", acceptEmpty = False ):
		keyboard = xbmc.Keyboard( default, title )
		while True:
			keyboard.doModal()
			if keyboard.isConfirmed():
				message = keyboard.getText().strip()
				if message == "":
					if acceptEmpty:
						return message
					else:
						self.alertMessageEmpty()
				elif len( message ) > twitter.CHARACTER_LIMIT:
					self.alertMessageTooLong()
				else:
					return message
			else:
				return None

	"""
	Description:
		Prompts the user to reply to a status
	Args:
		originalStatus::twitter.Status - status to which the user is replying
	Returns:
		Success - True
		Failure - False
		Cancel - None
	"""
	def reply( self, originalStatus ):
		screenName = originalStatus.GetUser().GetScreenName()
		message = self.promptMessage( self.lang.get( "Tweet_EnterStatus" ), "@" + screenName + " " )
		if message is None:
			return None
		else:
			return self.tweet( message )


	"""
	Description:
		Prompts the user for a screen name and message
		Sends the message if both fields are completed
	Returns:
		Accept: True
		Cancel: False
	"""
	def sendDirectMessage( self ):
		screenName = ""
		message = ""
		while True:
			screenName = self.promptScreenName( self.lang.get( "DirectMessage_Send_EnterUsername" ), screenName )
			if screenName is None:
				return None
			message = self.promptMessage( self.lang.get( "DirectMessage_Send_EnterMessage" ) %
																				{ 'userName' : screenName } )
			if message is not None:
				break
		try:
			self.api.PostDirectMessage( screenName, message )
			self.alertMessageSuccessfullySent()
			return True
		except:
			self.alertMessageNotSent()
			return False

	"""
	Description:
		Prompts the user for a message
		Sends the message if a non-empty message is entered
	Args:
		screenName::str - the recipient's screen name
	Returns:
		Accept: True
		Cancel: False
	"""
	def sendDirectMessage( self, userName ):
		message = self.promptMessage( self.lang.get( "DirectMessage_Send_EnterMessage" ) % locals() )
		if message is None:
				return
		try:
			self.api.PostDirectMessage( userName, message )
			self.alertMessageSuccessfullySent()
			return True
		except:
			self.alertMessageNotSent()
			return False

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
		Displays a menu with DirectMessage-related options
	"""
	def showMenu_DirectMessages( self ):
		menu = xbmcgui.Dialog()
		choice = 0
		while choice >= 0:
			options = self.menuOptions_DirectMessages
			choice = menu.select( self.lang.get( "Menu_DirectMessages_Title" ), options )
			if choice >= 0:
				action = self.menuOptions_DirectMessages[ choice ]
				if action == self.lang.get( "Menu_DirectMessages_Compose" ):
					self.sendDirectMessage()
				elif action == self.lang.get( "Menu_DirectMessages_Inbox" ):
					self.showMenu_DirectMessages_Inbox()
				elif action == self.lang.get( "Menu_DirectMessages_Sent" ):
					self.showMenu_DirectMessages_Sent()
				else:
					break

	"""
	Description:
		- Displays the user's Direct Message inbox
	"""
	def showMenu_DirectMessages_Inbox( self ):
		self.showMenu_DirectMessages_List( self.DirectMessageType[ 'received' ] )

	"""
	Description:
		- Displays a list of Direct Messages
	Args:
		messageType::self.DirectMessageType - "sent" or "received"
	"""
	def showMenu_DirectMessages_List( self, messageType ):
		dialog = xbmcgui.Dialog()
		choice = 0
		while choice >= 0:
			if messageType == self.DirectMessageType[ 'sent' ]:
				messages = self.api.GetDirectMessagesSent()
				header = self.lang.get( "DirectMessageListHeader_Sent" )
			else:
				messages = self.api.GetDirectMessages()
				header = self.lang.get( "DirectMessageListHeader_Received" )
			displayList = []
			for message in messages:
				display = self.formatDirectMessageDisplay( message, messageType )
				displayList.append( display )
			choice = dialog.select( header, displayList )
			if choice < 0 or choice >= len( messages ):
				break
			else:
				self.showMenu_DirectMessages_Selected( messages[ choice ], messageType )

	"""
	Description:
		 - Displays options that can be performed on a Direct Message
	Args:
		message::twitter.DirectMessage - currently selected message
		messageType::self.DirectMessageType - "sent" or "received"
	"""
	def showMenu_DirectMessages_Selected( self, message, messageType ):
		if messageType == self.DirectMessageType[ 'sent' ]:
			replyTo = message.GetRecipientScreenName()
		else:
			replyTo = message.GetSenderScreenName()
		options = [
			self.lang.get( "Menu_DirectMessages_Selected_Reply" ),
			self.lang.get( "Menu_DirectMessages_Selected_Delete" )
		]
		header = self.lang.get( "Menu_DirectMessages_Selected_HeaderFormat" ) % \
											{ "message" : self.formatDirectMessageDisplay( message, messageType ) }
		dialog = xbmcgui.Dialog()
		choice = 0
		while choice >= 0:
			choice = dialog.select( header, options )
			if choice >= 0:
				action = options[ choice ]
				if action == self.lang.get( "Menu_DirectMessages_Selected_Delete" ):
					if self.promptDeleteMessage( message ):
						break
				elif action == self.lang.get( "Menu_DirectMessages_Selected_Reply" ):
					self.sendDirectMessage( replyTo )

	"""
	Description:
		 - Displays the user's Direct Message outbox
	"""
	def showMenu_DirectMessages_Sent( self ):
		self.showMenu_DirectMessages_List( self.DirectMessageType[ 'sent' ] )

	"""
	Description:
		Displays the script's main menu
		Serves as the driver
	"""
	def showMenu_Main( self ):
		menu = xbmcgui.Dialog()
		choice = 0
		audioIsPlaying = False
		videoIsPlaying = False
		mediaIsPlaying = False
		while choice >= 0:
			options = self.menuOptions_Main
			audioIsPlaying = self.player.isPlayingAudio()
			videoIsPlaying = self.player.isPlayingVideo()
			if audioIsPlaying:
				options.insert( 0, self.lang.get( "MainMenu_Options_UpdateWithAudio" ) )
			elif videoIsPlaying:
				options.insert( 0, self.lang.get( "MainMenu_Options_UpdateWithVideo" ) )
			choice = menu.select( self.ApplicationNameWithVersion, options )
			if choice >= 0:
				action = options[ choice ]
				if action == self.lang.get( "MainMenu_Options_UpdateWithAudio" ) or \
					action == self.lang.get( "MainMenu_Options_UpdateWithVideo" ):
					self.tweetWhatImDoing()
				elif action == self.lang.get( "MainMenu_Options_UpdateManually" ):
					self.tweetManually()
				elif action == self.lang.get( "MainMenu_Options_ViewFriendsTimeline" ):
					self.viewFriendsTimeline()
				elif action == self.lang.get( "MainMenu_Options_DirectMessages" ):
					self.showMenu_DirectMessages()
				elif action == self.lang.get( "MainMenu_Options_EditAccount" ):
					self.editCredentials()
				elif action == self.lang.get( "MainMenu_Options_About" ):
					self.about()
				elif action == self.lang.get( "MainMenu_Options_Following" ):
					self.showMenu_UsersList( self.UsersListType[ "following" ] )
				elif action == self.lang.get( "MainMenu_Options_Followers" ):
					self.showMenu_UsersList( self.UsersListType[ "followers" ] )
				else:
					break
			if audioIsPlaying or videoIsPlaying:
				options.pop( 0 )

	"""
	Description:
		Shows a menu of user-specific options
	Args:
		user::twitter.User - the specified user
		listType::self.UsersListType - signifies the type of user list (following/follower)
	Returns:
		None
	"""
	def showMenu_User( self, user, listType ):
		userName = user.GetScreenName()
		optionMention = self.lang.get( "Menu_User_Mention" ) % locals()
		optionTimeline = self.lang.get( "Menu_User_ViewTimeline" ) % locals()
		optionDirectMessage = self.lang.get( "Menu_User_DirectMessage" )
		if listType == self.UsersListType[ "following" ]:
			header = self.lang.get( "Menu_User_Header_Following" ) % locals()
		else:
			header = self.lang.get( "Menu_User_Header_Follower" ) % locals()
		options = [
				optionMention
				, optionTimeline
				, optionDirectMessage
			]
		dialog = xbmcgui.Dialog()
		choice = 0
		while choice >= 0:
			choice = dialog.select( header, options )
			if choice >= 0:
				if options[ choice ] == optionMention:
					self.mention( user )
				elif options[ choice ] == optionTimeline:
					self.viewUserTimeline( user )
				elif options[ choice ] == optionDirectMessage:
					self.sendDirectMessage( user.GetScreenName() )

	def showMenu_UsersList( self, listType ):
		dialog = xbmcgui.Dialog()
		if listType == self.UsersListType[ "following" ]:
			users = self.api.GetFriends()
			header = self.lang.get( "MainMenu_Options_Following" )
		else:
			users = self.api.GetFollowers()
			header = self.lang.get( "MainMenu_Options_Followers" )
		displayList = []
		for user in users:
			displayList.append( user.GetScreenName() )
		choice = 0
		while choice >= 0:
			choice = dialog.select( header, displayList )
			if choice < 0 or choice >= len( users ):
				break
			else:
				self.showMenu_User( users[ choice ], listType )

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
		self.showMenu_Main()

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
					self.alertStatusTooLong()
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
		info = self.lang.get( "TweetMusic_MessageFormat" ) % { "artist" : song.getArtist(), "title" : song.getTitle() }
		message = act.appendFooterToStatus( info, twitter.CHARACTER_LIMIT, self.lang.get( "Tweet_Automatic_Suffix" ) )
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
		info = self.lang.get( "TweetVideo_MessageFormat" ).encode( "utf_8" ) % { "title" : title }
		message = act.appendFooterToStatus( info, twitter.CHARACTER_LIMIT, self.lang.get( "Tweet_Automatic_Suffix" ) )
		return self.tweet( message )

	"""
	Description:
		Displays the user's friends timeline
		This is the default view on the Twitter.com home page.
	"""
	def viewFriendsTimeline( self ):
		header = self.lang.get( "FriendsTimeline_Header" )
		statuses = self.api.GetFriendsTimeline()
		self.viewTimeline( header, statuses )

	"""
	Description:
		Displays a generic timeline of statuses
	Args:
		header::string - text to be used as the dialog's header
		statuses::twitter.Status[] - statuses to be displayed
	"""
	def viewTimeline( self, header, statuses ):
		displayList = []
		for status in statuses:
			userName = status.GetUser().GetScreenName()
			text = act.stripNewlines( status.GetText() )
			created = time.localtime( status.GetCreatedAtInSeconds() )
			timestamp = time.strftime( self.lang.get( "TimestampFormat" ), created )
			displayList.append( self.lang.get( "FriendsTimeline_StatusFormat" ) % locals() )
		while True:
			dialog = xbmcgui.Dialog()
			choice = dialog.select( header, displayList )
			if choice < 0 or choice >= len( statuses ):
				break
			else:
				self.reply( statuses[ choice ] )

	"""
	Description:
		Displays the specified user's timeline
		Alerts the user if the timeline is protected.
	Args:
		user::twitter.User - the user in question
	"""
	def viewUserTimeline( self, user ):
		userName = user.GetScreenName()
		header = self.lang.get( "UserTimeline_Header_Format" ) % locals()
		try:
			statuses = self.api.GetUserTimeline( user.GetScreenName() )
		except urllib2.HTTPError, e:
			if e.code == 401:
				self.alertTimelineProtected( user )
			else:
				raise
		else:
			self.viewTimeline( header, statuses )
