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
import auth
import crypt

cfg = sys.modules[ "__main__" ].cfg
i18n = sys.modules[ "__main__" ].i18n

class gui:
	"""Handles the scripts user interface"""

	"""
	Description:
		Default constructor
		Initializes the UI language
		Loads the user's credentials, if they are saved
	"""
	def __init__( self ):
		self.authentication = auth.Authentication()

		self.player = player = xbmc.Player()
		self.menuOptions_Main = [
			i18n( "MainMenu_Options_UpdateManually" )
			, i18n( "MainMenu_Options_ViewFriendsTimeline" )
			, i18n( "menu.main.options.search" )
			, i18n( "MainMenu_Options_Following" )
			, i18n( "MainMenu_Options_Followers" )
			, i18n( "menu.main.options.mentions" )
			, i18n( "MainMenu_Options_DirectMessages" )
			, i18n( "MainMenu_Options_EditAccount" )
			, i18n( "MainMenu_Options_About" )
			, i18n( "MainMenu_Options_Exit" )
		]
		self.menuOptions_DirectMessages = [
			i18n( "Menu_DirectMessages_Compose" )
			, i18n( "Menu_DirectMessages_Inbox" )
			, i18n( "Menu_DirectMessages_Sent" )
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
		self.ApplicationNameWithVersion = i18n( "ApplicationName" ) + ", v" + self.version

	"""
	Description:
		Displays the "About" dialog
	"""
	def about( self ):
		dialog = xbmcgui.Dialog()
		dialog.ok( cfg.get( "about.tagLine" ), sys.modules[ "__main__" ].__author__, cfg.get( "about.url" ), cfg.get( "about.email" ) )

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
			format = i18n( "DirectMessageDisplayFormat_Sent" )
		else:
			userName = message.GetSenderScreenName()
			format = i18n( "DirectMessageDisplayFormat_Received" )
		text = act.stripNewlines( message.GetText() )
		created = time.localtime( message.GetCreatedAtInSeconds() )
		timestamp = time.strftime( i18n( "TimestampFormat" ), created )
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
		message = self.promptMessage( i18n( "Tweet_EnterStatus" ), i18n( "Mention_Format" ) % locals() )
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
		sure = dialog.yesno( i18n( "DirectMessage_DeletePrompt_Header" ),
								i18n( "DirectMessage_DeletePrompt_Line1" ),
								i18n( "DirectMessage_DeletePrompt_Line2" ) )
		if sure:
			self.authentication.api.DestroyDirectMessage( message.GetId() )
			alert.directMessageDeleted()
		return sure

	"""
	Description:
		Generic input prompt
	Args:
		headerText::string (not None) - the header text to be displayed with the prompt
		defaultValue::string (not None) - the value used to prepopulate the prompt
		maskInput::bool (not None) - whether or not input characters should be masked, eg: passwords
	Returns:
		string - if user input is non-empty
		None - prompt is cancelled or input is empty
	"""
	def promptInput( headerText, defaultValue = "", maskInput = False ):
		defaultValue = defaultValue or ""
		keyboard = xbmc.Keyboard( defaultValue, headerText, maskInput )
		keyboard.doModal()
		if keyboard.isConfirmed():
			input = keyboard.getText().strip()
			if input:
				return input
		return None
	promptInput = staticmethod( promptInput )

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
						alert.messageEmpty()
				elif len( message ) > twitter.CHARACTER_LIMIT:
					alert.messageTooLong()
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
		message = self.promptMessage( i18n( "Tweet_EnterStatus" ), "@" + screenName + " " )
		if message is None:
			return None
		else:
			return self.tweet( message )

	"""
	Description:
		Allows the user to perform a search and view matching statuses
	Args:
		term::string - term to be searched for
	"""
	def search( self, term = None ):
		if not term:
			term = gui.promptInput( i18n( "search.input.heading" ) )
		if term:
			results = self.authentication.api.Search( term )
			heading = i18n( "search.results.heading.format" ) % { "searchTerm" : term }
			return self.viewTimeline( heading, results )

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
	def sendDirectMessage( self, userName = None ):
		if not userName:
			userName = self.promptInput( i18n( "DirectMessage_Send_EnterUsername" ) )
			if not userName:
				return False
		message = self.promptMessage( i18n( "DirectMessage_Send_EnterMessage" ) % locals() )
		if not message:
			return
		try:
			self.authentication.api.PostDirectMessage( userName, message )
			alert.messageSuccessfullySent()
			return True
		except:
			alert.messageNotSent()
			return False

	"""
	Description:
		Allows the user to perform a search and view matching statuses
	Args:
		term::string - term to be searched for
	"""
	def showMentions( self, username = None ):
		if not username:
			username = cfg.get( "auth.username" )
		username = "@" + username
		return self.search( username )

	"""
	Description:
		Displays a menu with DirectMessage-related options
	"""
	def showMenu_DirectMessages( self ):
		menu = xbmcgui.Dialog()
		choice = 0
		while choice >= 0:
			options = self.menuOptions_DirectMessages
			choice = menu.select( i18n( "Menu_DirectMessages_Title" ), options )
			if choice >= 0:
				action = self.menuOptions_DirectMessages[ choice ]
				if action == i18n( "Menu_DirectMessages_Compose" ):
					self.sendDirectMessage()
				elif action == i18n( "Menu_DirectMessages_Inbox" ):
					self.showMenu_DirectMessages_Inbox()
				elif action == i18n( "Menu_DirectMessages_Sent" ):
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
				messages = self.authentication.api.GetDirectMessagesSent()
				header = i18n( "DirectMessageListHeader_Sent" )
			else:
				messages = self.authentication.api.GetDirectMessages()
				header = i18n( "DirectMessageListHeader_Received" )
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
			i18n( "Menu_DirectMessages_Selected_Reply" ),
			i18n( "Menu_DirectMessages_Selected_Delete" )
		]
		header = i18n( "Menu_DirectMessages_Selected_HeaderFormat" ) % \
											{ "message" : self.formatDirectMessageDisplay( message, messageType ) }
		dialog = xbmcgui.Dialog()
		choice = 0
		while choice >= 0:
			choice = dialog.select( header, options )
			if choice >= 0:
				action = options[ choice ]
				if action == i18n( "Menu_DirectMessages_Selected_Delete" ):
					if self.promptDeleteMessage( message ):
						break
				elif action == i18n( "Menu_DirectMessages_Selected_Reply" ):
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
				options.insert( 0, i18n( "MainMenu_Options_UpdateWithAudio" ) )
			elif videoIsPlaying:
				options.insert( 0, i18n( "MainMenu_Options_UpdateWithVideo" ) )
			choice = menu.select( self.ApplicationNameWithVersion, options )
			if choice >= 0:
				action = options[ choice ]
				try:
					if action == i18n( "MainMenu_Options_UpdateWithAudio" ) or \
						action == i18n( "MainMenu_Options_UpdateWithVideo" ):
						self.tweetWhatImDoing()
					elif action == i18n( "MainMenu_Options_UpdateManually" ):
						self.tweetManually()
					elif action == i18n( "MainMenu_Options_ViewFriendsTimeline" ):
						self.viewFriendsTimeline()
					elif action == i18n( "MainMenu_Options_DirectMessages" ):
						self.showMenu_DirectMessages()
					elif action == i18n( "MainMenu_Options_EditAccount" ):
						self.authentication.authenticate( editing = True )
					elif action == i18n( "MainMenu_Options_About" ):
						self.about()
					elif action == i18n( "MainMenu_Options_Following" ):
						self.showMenu_UsersList( self.UsersListType[ "following" ] )
					elif action == i18n( "MainMenu_Options_Followers" ):
						self.showMenu_UsersList( self.UsersListType[ "followers" ] )
					elif action == i18n( "menu.main.options.search" ):
						self.search()
					elif action == i18n( "menu.main.options.mentions" ):
						self.showMentions()
					else:
						break
				except urllib2.URLError:
					alert.serverConnectionFailed()
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
		optionMention = i18n( "Menu_User_Mention" ) % locals()
		optionTimeline = i18n( "Menu_User_ViewTimeline" ) % locals()
		optionDirectMessage = i18n( "Menu_User_DirectMessage" )
		optionFollowing = i18n( "MainMenu_Options_Following" )
		optionFollowers = i18n( "MainMenu_Options_Followers" )
		options = [
				optionTimeline
				, optionMention
				, optionDirectMessage
				, optionFollowing
				, optionFollowers
			]
		dialog = xbmcgui.Dialog()
		choice = 0
		while choice >= 0:
			choice = dialog.select( userName, options )
			if choice >= 0:
				if options[ choice ] == optionMention:
					self.mention( user )
				elif options[ choice ] == optionTimeline:
					self.viewUserTimeline( user )
				elif options[ choice ] == optionDirectMessage:
					self.sendDirectMessage( user.GetScreenName() )
				elif options[ choice ] == optionFollowing:
					self.showMenu_UsersList( self.UsersListType[ "following" ], user.GetScreenName() )
				elif options[ choice ] == optionFollowers:
					self.showMenu_UsersList( self.UsersListType[ "followers" ], user.GetScreenName() )

	def showMenu_UsersList( self, listType = None, userName = None ):
		if not userName:
			userName = cfg.get( "auth.username" )
		dialog = xbmcgui.Dialog()
		if listType == self.UsersListType[ "following" ]:
			users = self.authentication.api.GetFriends( userName )
			header = i18n( "Menu_User_Header_Following" ) % locals()
		else:
			users = self.authentication.api.GetFollowers( userName )
			header = i18n( "Menu_User_Header_Followers" ) % locals()
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
		if self.authentication.authenticate():
			self.showMenu_Main()
		else:
			print "You must log in."
			return

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
			self.authentication.api.PostUpdate( message )
			alert.statusSuccessfullyUpdated()
			return True
		except:
			alert.serverConnectionFailed()
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
		keyboard = xbmc.Keyboard( "", i18n( "Tweet_EnterStatus" ) )
		while True:
			keyboard.doModal()
			if keyboard.isConfirmed():
				message = keyboard.getText().strip()
				if message == "":
					alert.statusEmpty()
				elif len( message ) > twitter.CHARACTER_LIMIT:
					alert.statusTooLong()
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
		info = i18n( "TweetMusic_MessageFormat" ) % { "artist" : song.getArtist(), "title" : song.getTitle() }
		message = act.appendFooterToStatus( info, twitter.CHARACTER_LIMIT, i18n( "Tweet_Automatic_Suffix" ) )
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
		info = i18n( "TweetVideo_MessageFormat" ).encode( "utf_8" ) % { "title" : title }
		message = act.appendFooterToStatus( info, twitter.CHARACTER_LIMIT, i18n( "Tweet_Automatic_Suffix" ) )
		return self.tweet( message )

	"""
	Description:
		Displays the user's friends timeline
		This is the default view on the Twitter.com home page.
	"""
	def viewFriendsTimeline( self ):
		header = i18n( "FriendsTimeline_Header" )
		statuses = self.authentication.api.GetFriendsTimeline()
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
			timestamp = time.strftime( i18n( "TimestampFormat" ), created )
			displayList.append( i18n( "FriendsTimeline_StatusFormat" ) % locals() )
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
		header = i18n( "UserTimeline_Header_Format" ) % locals()
		try:
			statuses = self.authentication.api.GetUserTimeline( user.GetScreenName() )
		except urllib2.HTTPError, e:
			if e.code == 401:
				alert.timelineProtected( user )
			else:
				raise
		else:
			self.viewTimeline( header, statuses )
