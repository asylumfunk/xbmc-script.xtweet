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

"""Project configuration"""

#Standard modules
import os
import sys
import xml.dom.minidom
#Project modules
import crypt

class Config:
	"""Handles project configuration settings"""

	_DEFAULT_VALUE = ""
	_FILE_DEFAULT = "settings.default.xml"
	_FILE_LEGACY_AUTHENTICATION = "settings.ini"
	_FILE_USER = "settings.user.xml"
	_KEY_ATTRIBUTE_NAME = "key"
	_KVP_TAG_NAME = "setting"
	_ROOT_TAG_NAME = "settings"

	def __init__( self ):
		directory = sys.modules[ "__main__" ].CONFIGURATION_DIRECTORY
		self.fileDefault = os.path.join( directory, self._FILE_DEFAULT )
		self.fileUser = os.path.join( directory, self._FILE_USER )
		self.reload()
		self._migrateLegacyAuthentication()

	"""
	Description:
		Reads the user's credentials from the configuration file
	Returns:
		Success: { USERNAME, PASSWORD }
		Failure: { None, None }
	"""
	def _loadCredentials( self, file ):
		try:
			file = open ( file, "r" )
			username = file.readline().strip()
			password = file.readline().strip()
		except:
			username = None
			password = None
		return username, password

	"""
	Description:
		Migrates authentication from the legacy system to the current system
		Removes the legacy file if it exists
	"""
	def _migrateLegacyAuthentication( self ):
		legacyFile = os.path.join( os.getcwd(), self._FILE_LEGACY_AUTHENTICATION )
		if os.path.isfile( legacyFile ):
			if not self.get( "auth.username" ):
				username, password = self._loadCredentials( legacyFile )
				username = username or ""
				password = crypt.en( password )
				self.set({
					"auth.username" : username,
					"auth.password" : password,
					"auth.method" : ""
				})
				self.save()
			os.remove( legacyFile )

	"""
	Description:
		Parses key-value pairs from a configuration file
	Args:
		file::string - absolute path of the input file
	Returns:
		dictionary - collection of key-value pairs from the input file
	"""
	def _parse( self, file ):
		data = {}
		if os.path.isfile( file ):
			try:
				doc = xml.dom.minidom.parse( file )
				root = doc.documentElement
				if ( not root or root.tagName != self._ROOT_TAG_NAME ):
					print "XML root not found: " + file
				kvps = root.getElementsByTagName( self._KVP_TAG_NAME )
				for kvp in kvps:
					key, value = self._parseKvp( kvp )
					if key:
						data[ key ] = value
				try:
					doc.unlink()
				except:
					print  "Unable to unlink file: " + file
			except:
				print "Unable to parse file: " + file
		else:
			print "File does not exist: " + file
		return data

	"""
	Description:
		Parses a key-value pair from an XML element node
	Args:
		kvp::XMLElementNode - a non-null element node to be parsed
	Returns:
		( key::string, value::string ) - the node's key-value data
	"""
	def _parseKvp( self, kvp ):
		value = self._DEFAULT_VALUE
		key = kvp.getAttribute( self._KEY_ATTRIBUTE_NAME )
		if key and kvp.hasChildNodes():
			value = kvp.firstChild.nodeValue
		return key, value

	"""
	Description:
		Retrieves the specified configuration setting
	Args:
		key::string - the key of the item to be retrieved
	Returns:
		string - value from user-specific settings OR default value OR None
	"""
	def get( self, key ):
		if key in self._settingsUser:
			return self._settingsUser[ key ]
		elif key in self._settingsDefault:
			return self._settingsDefault[ key ]
		else:
			return None

	"""
	Description:
		Reloads the configuration settings
	"""
	def reload( self ):
		self._settingsDefault = self._parse( self.fileDefault )
		self._settingsUser = self._parse( self.fileUser )

	"""
	Description:
		Writes the user-specific settings to its XML file
	"""
	def save( self ):
		implementation = xml.dom.minidom.getDOMImplementation()
		doc = implementation.createDocument( None, self._ROOT_TAG_NAME, None )
		for key, value in self._settingsUser.iteritems():
			ele = doc.createElement( self._KVP_TAG_NAME )
			text = doc.createTextNode( value )
			ele.setAttribute( self._KEY_ATTRIBUTE_NAME, key )
			ele.appendChild( text )
			doc.documentElement.appendChild( ele )
		try:
			file = open( self.fileUser , "w" )
			doc.writexml( file, encoding = "utf-8" )
		finally:
			file.close()

	"""
	Description:
		Sets the user-specific configuration settings
		Writes the settings to file
	Args:
		pairs::Dictionary - key-value pairs of user settings
	Returns:
		self
	"""
	def set( self, pairs ):
		if pairs:
			for key in pairs:
				self._settingsUser[ key ] = pairs[ key ]
			self.save()
		return self
