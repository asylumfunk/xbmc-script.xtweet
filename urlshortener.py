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
import urllib
import urllib2
#Project modules
from default import cfg

apiUrlFormat = cfg.get( "urlshortner.urlFormat" )

def create( longUrl ):
	queryParams = urllib.urlencode( { "url" : longUrl } )
	apiUrl = apiUrlFormat % { "params" : queryParams }
	request = urllib2.Request( url = apiUrl )
	try:
		stream = urllib2.urlopen( request )
		shortUrl = stream.read()
		return shortUrl
	except:
		return None
