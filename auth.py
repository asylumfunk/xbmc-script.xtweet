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
import urllib2
#Third-party modules
import twitter
import xbmc
#Project modules
import alert
import crypt
from default import cfg
from default import i18n

methods = { "basic" : "basic" , "oauth" : "oauth" }

"""
Handles API authentication
"""
class Authentication:

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
		edit::bool - if the user is editing existing credentials
	Returns:
		True::bool - the user successfully authenticated
		False::bool - the user did not successfully authenticate
	"""
	def authenticate( self, edit = False ):
		method = cfg.get( "auth.method" )
		if method == methods[ "oauth" ]:
			return self.authenticate_oauth( edit = edit )
		else:
			return self.authenticate_basic( edit = edit )

	"""
	Description:
		Performs Basic Authentication
	Args:
		edit::bool - if the user is editing existing credentials
	Returns:
		True::bool - the user successfully authenticated
		False::bool - the user did not successfully authenticate
	"""
	def authenticate_basic( self, edit = False ):
		username, password = self.getUsernameAndPassword()
		isValid = False
		if edit or not username or not password:
			needsVerified = False
		else:
			needsVerified = True
		while not isValid:
			if needsVerified:
				api = twitter.Api( username, password )
				if self.verifyCredentials( api ):
					self.api = api
					self.setUsernameAndPassword( username, password )
					return True
				else:
					alert.invalidUsernamePassword()
			username, password = self.promptUsernameAndPassword()
			if not username or not password:
				return False
			else:
				needsVerified = True

	def authenticate_oauth( self ):
		raise Error( "Not Implemented Yet!" )

	"""
	Description:
		Retrieves the user's current username and password
	Returns:
		( username, password ) - a tuple of the user's current username and password
	"""
	def getUsernameAndPassword( self ):
		username = cfg.get( "auth.username" )
		password = cfg.get( "auth.password" )
		password = crypt.de( password )
		return username, password

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
	def promptInput( self, headerText, defaultValue = "", maskInput = False ):
		defaultValue = defaultValue or ""
		keyboard = xbmc.Keyboard( defaultValue, headerText, maskInput )
		keyboard.doModal()
		if keyboard.isConfirmed():
			input = keyboard.getText().strip()
			if input:
				return input
		return None

	"""
	Description:
		Prompts for a password
	Returns:
		Accept: the user-supplied input
		Cancel: None
	"""
	def promptPassword( self ):
		return self.promptInput( headerText = i18n( "EnterPassword" ), maskInput = True )

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
		return self.promptInput( headerText = i18n( "EnterUsername" ), defaultValue = username )

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
				"auth.method" : newMethod
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
	"""
	def verifyCredentials( self, api ):
		try:
			user = api.VerifyCredentials()
			if user and user.GetScreenName():
				self.isAuthenticated = True
				return True
		except urllib2.HTTPError, e:
			if e.code == 401:
				pass
			else:
				raise
		return False