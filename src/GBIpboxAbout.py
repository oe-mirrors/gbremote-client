#############################################################################
#
# Copyright (C) 2014 Impex-Sat Gmbh & Co.KG
# Written by Sandro Cavazzoni <sandro@skanetwork.com>
# All Rights Reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
#############################################################################

from Screens.Screen import Screen
from Screens.MessageBox import MessageBox

from Components.ActionMap import ActionMap
from Components.Label import Label

from GBIpboxLocale import _
from boxbranding import getImageDistro

class GBIpboxAbout(Screen):
	skin = """
			<screen position="360,150" size="560,400">
				<widget name="about"
						position="10,10"
						size="540,340"
						font="Regular;22"
						zPosition="1" />
			</screen>"""
			
	def __init__(self, session):
		Screen.__init__(self, session)

		if getImageDistro() in ("openatv"):
			self.setTitle(_('IPBOX Client About'))
			about = "IPBOX Client 1.0""\n"
		else:
			self.setTitle(_('GBIpbox Client About'))
			about = "GBIpbox Client 1.0""\n"

		about += "(c) 2014 Impex-Sat Gmbh & Co.KG\n\n"
		about += "Written by Sandro Cavazzoni <sandro@skanetwork.com>"
		
		self['about'] = Label(about)
		self["actions"] = ActionMap(["SetupActions"],
		{
			"cancel": self.keyCancel
		})
		
	def keyCancel(self):
		self.close()