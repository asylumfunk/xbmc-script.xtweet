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

#Third-party modules
import sys
import xbmcgui

i18n = sys.modules[ "__main__" ].i18n

"""
Description:
	Displays a generic OK prompt
Args:
	heading::string - heading text (optional)
	line1::string - first line of display text (optional)
	line2::string - second line of display text (optional)
	line3::string - third line of display text (optional)
"""
def _ok( heading = "", line1 = "", line2 = "", line3 = "" ):
	dialog = xbmcgui.Dialog()
	return dialog.ok( heading, line1, line2, line3 )

"""
Description:
	Alerts the user that the Direct Message has been deleted
"""
def directMessageDeleted( self ):
	return _ok( i18n( "Success" ), i18n( "Message_Alert_DirectMessage_Deleted" ) )

"""
Description:
	Alerts the user that the supplied OAuth PIN is invalid
"""
def invalidOAuthPin():
	return _ok( i18n( "Warning" ), "The PIN could not be authorized.", "Please try again." )

"""
Description:
	Alerts the user that the supplied username/password combination is invalid
"""
def invalidUsernamePassword():
	return _ok( i18n( "Warning" ), i18n( "alert.invalidUsernamePassword" ), i18n( "alert.tryAgain" ) )

"""
Description:
	Alerts the user that their message cannot be empty
"""
def messageEmpty( self ):
	return _ok( i18n( "Warning" ), i18n( "Message_Alert_Empty_Text" ) )

"""
Description:
	Alerts the user that their message could not be sent
"""
def messageNotSent( self ):
	return _ok( i18n( "Warning" ), i18n( "Message_Alert_NotSent1" ), i18n( "Message_Alert_NotSent2" ), i18n( "Message_Alert_NotSent3" ) )

"""
Description:
	Alerts the user that their message was successfully sent
"""
def messageSuccessfullySent( self ):
	return _ok( i18n( "Success" ), i18n( "Message_Alert_SentSuccessfully" ) )

"""
Description:
	Alerts the user that their message cannot exceed the maximum length
"""
def messageTooLong( self ):
	return _ok( i18n( "Warning" ), i18n( "Message_Alert_TooLong_Text" ) %
																						{ "maxLength" : twitter.CHARACTER_LIMIT } )

"""
Description:
	Alerts the user that the authentication message could not be sent
"""
def oauthMessageNotSent():
	return _ok( i18n( "Warning" ), i18n( "auth.oauth.sendAuthorizationMessage.line1" ), i18n( "auth.oauth.sendAuthorizationMessage.line2" ) )

"""
Description:
	Alerts the user that Twitter.com could not be reached
"""
def serverConnectionFailed( self ):
	return _ok( i18n( "Warning" ), i18n( "Server_ConnectionFailed_Line1" ), i18n( "Server_ConnectionFailed_Line2" ), i18n( "Server_ConnectionFailed_Line3" ) )

"""
Description:
	Alerts the user that their status cannot be empty
"""
def statusEmpty( self ):
	return _ok( i18n( "Warning" ), i18n( "Tweet_Alert_Empty_Text" ) )

"""
Description:
	Alerts the user that their status was successfully updated
"""
def statusSuccessfullyUpdated( self ):
	return _ok( i18n( "Success" ), i18n( "Tweet_Alert_Success_Text" ) )

"""
Description:
	Alerts the user that their status cannot exceed the maximum length
"""
def statusTooLong( self ):
	return _ok( i18n( "Warning" ), i18n( "Tweet_Alert_TooLong_Text" ) %
																			{ "maxLength" : twitter.CHARACTER_LIMIT } )

"""
Description:
	Alerts the user that the requested user timeline is protected
"""
def timelineProtected( self, user ):
	return _ok( i18n( "UserTimeline_Protected_Header_Format" ) % { 'userName' : user.GetScreenName() },
				i18n( "UserTimeline_Protected_Line1" ),
				i18n( "UserTimeline_Protected_Line2" ) )
