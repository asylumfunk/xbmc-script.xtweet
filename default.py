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

 #xTweet, an XBMC script to interface with Twitter

#Standard modules
import os
import shutil
import sys

#Script constants
__author__ = "asylumfunk"
__author_url__ = "https://github.com/asylumfunk"
__scriptname__ = "xTweet"
__url__ = "https://github.com/asylumfunk/xbmc-xtweet"
__version__ = "1.4"

PROJECT_DIRECTORY = os.getcwd().replace( ";", "" )
RESOURCE_DIRECTORY = os.path.join( PROJECT_DIRECTORY, "resources" )
CACHE_DIRECTORY = os.path.join( RESOURCE_DIRECTORY, "cache" )
CONFIGURATION_DIRECTORY = os.path.join( RESOURCE_DIRECTORY, "config" )
LANGUAGE_DIRECTORY = os.path.join( RESOURCE_DIRECTORY, "language" )
SOURCE_DIRECTORY = os.path.join( RESOURCE_DIRECTORY, "lib" )
UPDATES_DIRECTORY = os.path.join( RESOURCE_DIRECTORY, "updates" )
sys.path.append( SOURCE_DIRECTORY )
sys.path.append( os.path.join( SOURCE_DIRECTORY, "python-twitter" ) )
sys.path.append( os.path.join( SOURCE_DIRECTORY, "oauth-python" ) )
sys.path.append( os.path.join( SOURCE_DIRECTORY, "oauth-python-twitter" ) )

"""
Description:
	Safely cleans up the mess left by previous installs
Note:
	Version 1.5 restructured the project layout.
	I intend on removing this code after a few more releases (2.0 maybe?).
	Users who make a big upgrade leap (1.4 -> 2.0/1), could experience difficulties.
	However, I'm HOPING those numbers will be small and a clean install will remedy the problem.
"""
def cleanupLegacyInstall():
	tryMoveUserSettings()
	tryRemoveDeprecatedFiles()

"""
Description:
	Previously, the user settings file resided in the base directory.
	If the file is still saved there, we will move it to its new location.
"""
def tryMoveUserSettings():
	userSettings = "settings.user.xml"
	oldUserSettings = os.path.join( PROJECT_DIRECTORY, userSettings )
	if os.path.isfile( oldUserSettings ):
		newUserSettings = os.path.join( CONFIGURATION_DIRECTORY, userSettings )
		os.rename( oldUserSettings, newUserSettings )

"""
Description:
	Removes deprecated files and directories from the base directory.
TODO:
	I may want a try-catch on this guy.
"""
def tryRemoveDeprecatedFiles():
	keep = set ( [ "CHANGES.xml", "COPYING", "default.py", "default.tbn", "LICENSE", "NOTICE", "README.txt", "resources", "settings.ini", "settings.user.xml", ".svn" ] )
	contents = set( os.listdir( PROJECT_DIRECTORY ) )
	trash = ( contents | keep ) ^ keep
	for path in trash:
		path = os.path.join( PROJECT_DIRECTORY, path )
		if os.path.isfile( path ):
			os.remove( path )
		elif os.path.isdir( path ):
			shutil.rmtree( path )
	tryRemoveSvn()

"""
Description:
	"Guesses" if the project is under version control, and removes an .svn entry if it is unlikely
Note:
	This is pretty gnarly; I admit it and appologize.
	The v1.3 release mistakenly included the svn files (among others) in the archive.
	All but one entry are removed along with the project restructuring.
	We guess if the final should be removed, if the "resources" directory is not under version control.
"""
def tryRemoveSvn():
	svnRoot = os.path.join( PROJECT_DIRECTORY, ".svn" )
	if os.path.isdir( svnRoot ):
		svnResources = os.path.join( RESOURCE_DIRECTORY, ".svn" )
		if not os.path.isdir( svnResources ):
			print "removing svn..."
			#TODO: restore this when tested on unversioned directory
			shutil.rmtree( svnRoot )

#Only start the gui if this module is executed directly
if __name__ == "__main__":
	cleanupLegacyInstall()
	import config
	import lang
	cfg = config.Config()
	i18n = lang.Lang().get
	import update
	u = update.Update()
	if not u.tryUpdateProject() or not u.requiresRestart():
		print "booting..."
		#import gui
		#ui = gui.gui()
		#ui.start()
	else:
		print "restarting..."
