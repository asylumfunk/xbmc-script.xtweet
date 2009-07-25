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
import xbmcgui
#Project modules
from default import i18n

def oauthMessageNotSent():
	dialog = xbmcgui.Dialog()
	return dialog.ok( i18n( "Warning" ), i18n( "auth.oauth.sendAuthorizationMessage.line1" ), i18n( "auth.oauth.sendAuthorizationMessage.line2" ) )

"""
Description:
	Alerts the user that the supplied OAuth PIN is invalid
"""
def invalidOAuthPin():
		dialog = xbmcgui.Dialog()
		return dialog.ok( i18n( "Warning" ), "The PIN could not be authorized.", "Please try again." )

"""
Description:
	Alerts the user that the supplied username/password combination is invalid
"""
def invalidUsernamePassword():
		dialog = xbmcgui.Dialog()
		return dialog.ok( i18n( "Warning" ), i18n( "alert.invalidUsernamePassword" ), i18n( "alert.tryAgain" ) )