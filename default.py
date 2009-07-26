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
import sys
#Third-party modules
sys.path.append( os.path.join( os.getcwd(), "python-twitter-0.6" ) )
sys.path.append( os.path.join( os.getcwd(), "oauth-python" ) )
sys.path.append( os.path.join( os.getcwd(), "oauth-python-twitter" ) )
#Project modules
import config
import lang

#Script constants
__author__ = "asylumfunk"
__author_url__ = "https://github.com/asylumfunk"
__scriptname__ = "xTweet"
__url__ = "https://github.com/asylumfunk/xbmc-xtweet"
__version__ = "1.4"

cfg = config.Config()
i18n = lang.Lang().get

#Only start the gui if this module is executed directly
if __name__ == "__main__":
	import gui
	ui = gui.gui()
	ui.start()