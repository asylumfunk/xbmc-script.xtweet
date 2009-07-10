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

About_TagLine = "Half monkey, half zombie, half amazing"
About_Email = "@asylumfunk"
About_Url = "https://github.com/asylumfunk"
ConfigFile = "settings.ini"
Status_Truncation = "..."

"""
Description:
	Reads the user's credentials from the configuration file
Returns:
	Success: { USERNAME, PASSWORD }
	Failure: { None, None }
"""
def loadCredentials():
	try:
		file = open (os.path.join( os.getcwd(), ConfigFile ), "r" )
		username = file.readline().strip()
		password = file.readline().strip()
	except:
		username = None
		password = None
	return username, password

"""
Description:
	Saves the user's credentials to the configuration file
Returns:
	Boolan : success flag
"""
def saveCredentials( username, password ):
	try:
		file = open( os.path.join( os.getcwd(), ConfigFile ), "w" )
		file.write( username + "\n" + password )
	except:
		file.close()
		return False
	else:
		file.close()
		return True