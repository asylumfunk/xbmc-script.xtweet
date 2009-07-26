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

"""Business logic layer"""

#Standard modules
import os
import sys
import time
#Project modules
import config

cfg = sys.modules[ "__main__" ].cfg
i18n = sys.modules[ "__main__" ].i18n

"""Represents a type of direct message"""
DirectMessageType = {
	"sent" : 1,
	"received" : 2
}

"""
Description:
	Appends the default footer to the status
	If necessary, mesage is truncated to fit the footer
Args:
	message::string : original status (without footer)
	maxLength::int : maximum status length (including footer)
Returns:
	string : new status (including footer), <= maxLength
"""
def appendFooterToStatus( message, maxLength, suffix ):
	status = message + " " + suffix
	if len( status ) > maxLength:
		truncator = cfg.get( "status.truncation" )
		status = message[ 0 : ( maxLength - len( suffix ) - len( truncator ) - 1 ) ] + truncator + " " + suffix
	return status

"""
Description:
	Formats the display string for a direct message
Args:
	message::twitter.DirectMessage - the message to be displayed
	messageType::DirectMessageType - "sent" or "received"
Returns:
	string - the properly formatted direct message string
"""
def formatDirectMessageDisplay( message, messageType ):
	if messageType == DirectMessageType[ 'sent' ]:
		userName = message.GetRecipientScreenName()
		format = i18n( "DirectMessageDisplayFormat_Sent" )
	else:
		userName = message.GetSenderScreenName()
		format = i18n( "DirectMessageDisplayFormat_Received" )
	text = stripNewlines( message.GetText() )
	created = time.localtime( message.GetCreatedAtInSeconds() )
	timestamp = time.strftime( i18n( "TimestampFormat" ), created )
	return format % locals()

"""
Description:
	Parses the base filename (without extension) from a path name
Args:
	file::string : the file's path
Returns:
	string : the base filename (without extension) of the path
"""
def parseTitleFromFilename( file ):
		return os.path.splitext( os.path.split( file )[ 1 ] )[ 0 ]

"""
Description:
	Strips newline characters from the input string
Args:
	text::string - input text
	[replacementString::string = " "] - string used to replace newlines
Returns:
	None if input is None
	Else, text with all newline instances replaced by the replacement string
"""
def stripNewlines( text, replacementString = " " ):
	if text is None:
		return text
	else:
		return text.replace( "\n", replacementString )