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

from Components.Console import Console
from Components.config import config

import os

mountstate = False
mounthost = None

class GBIpboxMount:
	def __init__(self, session):
		self.session = session
		self.console = Console()
		if os.path.exists('/media/hdd') or os.system('mount |grep -i /media/hdd') == 0:
			self.mountpoint = '/media/net/IpBox'
		else:
			self.mountpoint = '/media/hdd'
		self.share = 'Harddisk'

	def automount(self):
		global mountstate
		global mounthost
		mountstate = False
		mounthost = None
		if config.ipboxclient.mounthdd.value:
			if self.isMountPoint(self.mountpoint):
				if not self.umount(self.mountpoint):
					print 'Cannot umount ' + self.mounpoint
					return

			if not self.mount(config.ipboxclient.host.value, self.share, self.mountpoint):
				print 'Cannot mount ' + config.ipboxclient.host.value + '/' + self.share + ' to ' + self.mountpoint
			else:
				mountstate = True
				mounthost = config.ipboxclient.host.value

	def remount(self):
		global mountstate
		global mounthost
		if mountstate and not config.ipboxclient.mounthdd.value:
			self.umount(self.mountpoint)
			mountstate = False
		elif not mountstate and config.ipboxclient.mounthdd.value:
			self.automount()
		elif mountstate and config.ipboxclient.mounthdd.value != mounthost:
			self.automount()
	
	def isMountPoint(self, path):
		return os.system('mountpoint ' + path) == 0
		
	def umount(self, path = None):
		return os.system('umount ' + path) == 0
		
	def mount(self, ip, share, path):
		try:
			os.makedirs(path)
		except Exception:
			pass
		return os.system('mount -t cifs -o rw,nolock,noatime,noserverino,iocharset=utf8,vers=2.0,username=guest,password= //' + ip + '/' + share + ' ' + path) == 0
