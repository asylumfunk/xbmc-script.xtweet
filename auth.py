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

#Standard modules
import sys
import urllib2
#Third-party modules
import oauthtwitter
import twitter
import xbmc
import xbmcgui
#Project modules
import alert
import crypt
import gui
import urlshortener

cfg = sys.modules[ "__main__" ].cfg
i18n = sys.modules[ "__main__" ].i18n

methods = { "basic" : "basic" , "oauth" : "oauth" }

"""
Handles API authentication
"""
class Authentication:

	_consumerKey = crypt.de( cfg.get( "auth.consumerKey" ) )
	_consumerSecret = crypt.de( cfg.get( "auth.consumerSecret" ) )

	"""
	Description:
		Default constructor
	"""
	def __init__( self ):
		self.isAuthenticated = False
		self.api = None

	"""
	Description:
		Performs either Basic or OAuth Authentication, dependent upon user's settings
	Args:
		editing::bool - if the user is editing existing credentials
	Returns:
		True::bool - the user successfully authenticated
		False::bool - the user did not successfully authenticate
	"""
	def authenticate( self, editing = False ):
		method = cfg.get( "auth.method" )
		if not editing and method == methods[ "oauth" ]:
			self.authenticate_oauth()
		else:
			if self.authenticate_basic( editing = editing ):
				if editing or not method:
					if self.promptUseOAuth():
						self.authenticate_oauth()
		return self.isAuthenticated

	"""
	Description:
		Performs Basic Authentication
	Args:
		editing::bool - if the user is editing existing credentials
	Returns:
		True::bool - the user successfully authenticated
		False::bool - the user did not successfully authenticate
	"""
	def authenticate_basic( self, editing ):
		username, password = self.getUsernameAndPassword()
		isValid = False
		if editing or not username or not password:
			needsVerified = False
		else:
			needsVerified = True
		while not isValid:
			if needsVerified:
				api = twitter.Api( username, password )
				if self.verifyCredentials( api ):
					self.setUsernameAndPassword( username, password )
					return True
				else:
					alert.invalidUsernamePassword()
			username, password = self.promptUsernameAndPassword()
			if not username or not password:
				return False
			else:
				needsVerified = True

	"""
	Description:
		Performs OAuth Authentication
	Returns:
		True::bool - the user successfully authenticated
		False::bool - the user did not successfully authenticate
	"""
	def authenticate_oauth( self ):
		accessToken = self.getAccessToken()
		if accessToken:
			api = oauthtwitter.OAuthApi( self._consumerKey, self._consumerSecret, accessToken )
			if self.verifyCredentials( api ):
				return True
			else:
				alert.invalidOAuthPin()
				if not self.authenticate_basic( editing = True ):
					return False
		requestToken, authorizationUrl = self.generateTokenAndUrl()
		if not self.sendAuthorizationMessage( authorizationUrl ):
			return False
		self.displayOAuthInstructions()
		while True:
			pin = self.promptPin()
			if not pin:
				return False
			else:
				accessToken = self.requestAccessToken( requestToken, pin )
				if accessToken:
					api = oauthtwitter.OAuthApi( self._consumerKey, self._consumerSecret, accessToken )
					if self.verifyCredentials( api ):
						self.setAccessToken( accessToken )
						return True
				alert.invalidOAuthPin()

	"""
	Description:
		Displays OAuth instructions
	"""
	def displayOAuthInstructions( self ):
		instructions = xbmcgui.Dialog()
		return instructions.ok( i18n( "auth.secureLogin.heading" ) , i18n( "auth.secureLogin.instructions.line1" ), i18n( "auth.secureLogin.instructions.line2" ), i18n( "auth.secureLogin.instructions.line3" ) )

	"""
	Description:
		Generates an OAuth request token and authorization url
	Returns:
		( requestToken::oauthtwitter.oauth.OAuthToken, authorizationUrl::string )
	"""
	def generateTokenAndUrl( self ):
		api = oauthtwitter.OAuthApi( self._consumerKey, self._consumerSecret )
		requestToken = api.getRequestToken()
		authorizationUrl = api.getAuthorizationURL( requestToken )
		return requestToken, authorizationUrl

	"""
	Description:
		Retrieves the user's OAuth access token
	Returns:
		if the value exists:
			oauthtwitter.oauth.OAuthToken - the user's OAuth access token
		else:
			None
	"""
	def getAccessToken( self ):
		tokenString = crypt.de( cfg.get( "auth.accessToken" ) )
		if tokenString:
			return oauthtwitter.oauth.OAuthToken.from_string( tokenString )
		else:
			return None

	"""
	Description:
		Retrieves the user's current username and password
	Returns:
		( username, password ) - a tuple of the user's current username and password (plain-text)
	"""
	def getUsernameAndPassword( self ):
		username = cfg.get( "auth.username" )
		password = cfg.get( "auth.password" )
		password = crypt.de( password )
		return username, password

	"""
	Description:
		Prompts for a password
	Returns:
		Accept: the user-supplied input
		Cancel: None
	"""
	def promptPassword( self ):
		return gui.gui.promptInput( headerText = i18n( "EnterPassword" ), maskInput = True )

	"""
	Description:
		Prompts the user to enter their authorization PIN
	Returns:
		Accept: str - the PIN
		Cancel: None
	"""
	def promptPin( self ):
		prompt = xbmcgui.Dialog()
		ShowAndGetNumber = 0
		pin = prompt.numeric( ShowAndGetNumber, i18n( "auth.promptPin.heading" ) )
		if pin:
			return pin
		else:
			return None

	"""
	Description:
		Prompts the user to see if they want to use OAuth
	Returns:
		bool - whether or not the user wants to use OAuth
	"""
	def promptUseOAuth( self ):
		prompt = xbmcgui.Dialog()
		return prompt.yesno( i18n( "auth.secureLogin.heading" ), i18n( "auth.secureLogin.prompt.line1" ), i18n( "auth.secureLogin.prompt.line2" ), i18n( "auth.secureLogin.prompt.line3" ) )

	"""
	Description:
		Prompts for a username
	Args:
		username::string - the user's current username
	Returns:
		Accept: the user-supplied input
		Cancel: None
	"""
	def promptUsername( self, username ):
		return gui.gui.promptInput( headerText = i18n( "EnterUsername" ), defaultValue = username )

	"""
	Description:
		Prompts for a username and password
	Returns:
		( username, password ) - if  both are entered
		( None, None ) - if the prompt is cancelled
	"""
	def promptUsernameAndPassword( self ):
		username = cfg.get( "auth.username" )
		while True:
			username = self.promptUsername( username )
			if not username:
				return None, None
			password = self.promptPassword()
			if password:
				return username, password

	"""
	Description:
		Requests an OAuth access token
	Args:
		requestToken::oauthtwitter.oauth.OAuthToken - the user's OAuth request token
		pin::int - the user's validation PIN
	Returns:
		if successful:
			oauthtwitter.oauth.OAuthToken - the user's OAuth access token
		else:
			None
	"""
	def requestAccessToken( self, requestToken, pin ):
		try:
			api = oauthtwitter.OAuthApi( self._consumerKey, self._consumerSecret, requestToken )
			accessToken = api.getAccessToken( pin )
			return accessToken
		except urllib2.HTTPError, e:
			if e.code == 401:
				return None
			else:
				raise

	"""
	Description:
		Sends an authorization message to the user's account
	Args:
		authorizationUrl::string - a Twitter.com authorization url
	"""
	def sendAuthorizationMessage( self, authorizationUrl ):
		username = cfg.get( "auth.username" )
		shortUrl = urlshortener.create( authorizationUrl )
		if shortUrl:
			message = i18n( "auth.oauth.sendAuthorizationMessage.messageFormat" ) % { "url" : shortUrl }
		else:
			message = authorizationUrl
		try:
			self.api.PostDirectMessage( username, message )
			return True
		except:
			alert.oauthMessageNotSent()
			return False

	"""
	Description:
		Sets the user's OAuth access token
	Args:
		accessToken::oauthtwitter.oauth.OAuthToken - the user's OAuth access token
	"""
	def setAccessToken( self, accessToken ):
		cfg.set({
			"auth.accessToken" : crypt.en( str( accessToken ) ),
			"auth.method" : methods[ "oauth" ],
			"auth.password" : ""
		})

	"""
	Description:
		Updates the user configuration if values have changed
	Args:
		newUsername::string - new username
		newPassword::string - new, plaintext password
	Returns:
		True::bool - the configuration was updated
		False::bool - the configuration was not updated
	"""
	def setUsernameAndPassword( self, newUsername, newPassword ):
		oldUsername, oldPassword = self.getUsernameAndPassword()
		oldMethod = cfg.get( "auth.method" )
		newMethod = methods[ "basic" ]
		if newUsername != oldUsername or \
		newPassword != oldPassword or \
		newMethod != methods[ "basic" ]:
			cfg.set({
				"auth.username" : newUsername,
				"auth.password" : crypt.en( newPassword ),
				"auth.method" : newMethod,
				"auth.accessToken" : ""
			})
			return True
		else:
			return False

	"""
	Description:
		Verifies that the user has access to the requested account
	Args:
		api::twitter.Api - the API used for verification
	Returns:
		True::bool - user has access to the account
		False::bool - user does not have access to the account
	TODO:
		add a progress bar while waiting
	"""
	def verifyCredentials( self, api ):
		progress = xbmcgui.DialogProgress()
		progress.create( i18n( "auth.verifyCredentials.heading" ), i18n( "auth.verifyCredentials.line1" ) )
		try:
			user = api.VerifyCredentials()
			if user and user.GetScreenName():
				self.isAuthenticated = True
				self.api = api
				progress.update( 100 )
				return True
		except urllib2.HTTPError, e:
			if e.code == 401:
				pass
			else:
				progress.update( 100 )
				raise
		progress.update( 100 )
		return False
