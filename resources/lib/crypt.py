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
import base64

"""
Description:
	Decodes a Base64 string
Args:
	text::string - a Base64 encoded string
Returns:
	string - decoded representation of the Base64 string
"""
def de( text ):
	if text:
		return base64.b64decode( text )
	else:
		return text

"""
Description:
	Encodes a Base64 string
Args:
	text::string - a string
Returns:
	string - Base64 representation of the string
"""
def en( text ):
	if text:
		return base64.b64encode( text )
	else:
		return text
