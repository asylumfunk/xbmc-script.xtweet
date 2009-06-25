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
import os
import sys
import xml.dom.minidom
#Third-party modules
import xbmc

class lang:
	"""Handles all of the user facing text and i18n
	Public attributes:
		language::string
	Public methods:
		get( key::string )::string
	"""

	"""
	Description:
		Initializes the strings used for user-facing text
		Attempts to use the system's language, if available
		Falls back to English if the native language is unavailable
	Args:
		rootDir : string : the script's root directory
	"""
	def __init__( self ):
		self.rootDir = os.getcwd()
		self.defaultLanguage = "english"
		self.language = None
		self.file = None
		self.strings = { }
		self.initSupportedLanguage()
		if self.language is not None:
			self.load()

	"""
	Description:
		Retrieves the string represented by the provided key
	Args:
		key::string : represents the string to be retrieved
	Returns:
		string : the corresponding value
	"""
	def get( self, key ):
		return self.strings.get( key )

	"""
	Description:
		Attempts to use the system's language, if available
		Falls back to English if the native language is unavailable
	Returns:
		self
	TODO:
		we need an elegant way to bail out if a language file cannot be located (program is unusable)
	"""
	def initSupportedLanguage( self ):
		if not self.set( xbmc.getLanguage().lower() ):
			if not self.set( self.defaultLanguage ):
				self.set( None )
				print "Unable to load the default language file: " + self.defaultLanguage
		return self

	"""
	Description:
		determines whether or not the current language is supported
	Returns:
		boolean : whether or not the current language is supported
	"""
	def isSupported( self ):
		return self.language is not None and os.path.isfile( self.file )

	"""
	Description:
		loads the object's language file and all corresponding strings
	Returns:
		self
	TODO:
		we need an elegant way to bail out if a language file cannot be located (program is unusable)
	"""
	def load( self ):
		doc = xml.dom.minidom.parse( self.file )
		root = doc.documentElement
		if ( not root or root.tagName != "strings" ):
			self.set( None )
			print "Unable to parse the language file: " + self.language
		strings = root.getElementsByTagName( "string" )
		for string in strings:
			key = string.getAttribute( "key" )
			if ( key not in self.strings and string.hasChildNodes() ):
				self.strings[ key ] = string.firstChild.nodeValue
		try:
			doc.unlink()
		except:
			print  "Unable to unlink the language file"
		return self

	"""
	Description:
		Stores the specified language name internally
		Calculates and stores the language file path
	Args:
		language::string : name of the language
	Returns:
		boolean : whether or not the language is supported
	"""
	def set( self, language ):
		self.language = language

		if language is None:
			self.file = None
			return False
		else:
			self.file = self.theFile( language )
			return self.isSupported()

	"""
	Description:
		calculates the path of the specified language file
	Args:
		language::string : name of the language file to be calculated
	Returns:
		string : absolute path of the language file
	"""
	def theFile( self, language ):
		return os.path.join( self.rootDir, "language", language, "strings.xml" )