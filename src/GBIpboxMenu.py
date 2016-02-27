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
from Screens.Standby import TryQuitMainloop

from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.ConfigList import ConfigListScreen
from Components.config import config, getConfigListEntry, ConfigSubsection, ConfigInteger, ConfigYesNo, ConfigText
from Components.Sources.Boolean import Boolean
from Components.Sources.StaticText import StaticText

from GBIpboxDownloader import GBIpboxDownloader
from GBIpboxScan import GBIpboxScan
from GBIpboxAbout import GBIpboxAbout
from GBIpboxMount import GBIpboxMount
from GBIpboxLocale import _
from boxbranding import getImageDistro

from enigma import eTimer

class GBIpboxMenu(Screen, ConfigListScreen):
	skin = """
		<screen position="360,150" size="560,400">
			<widget name="config"
					position="10,10"
					zPosition="3"
					size="540,270"
					scrollbarMode="showOnDemand"
					transparent="1">
			</widget>

			<widget source="text"
					render="Label"
					position="10,290"
					size="540,60"
					font="Regular;20" />

			<widget name="key_red"
					position="0,360"
					size="140,40"
					valign="center"
					halign="center"
					zPosition="5"
					transparent="1"
					foregroundColor="white"
					font="Regular;18" />
					
			<widget name="key_green"
					position="140,360"
					size="140,40"
					valign="center"
					halign="center"
					zPosition="5"
					transparent="1"
					foregroundColor="white"
					font="Regular;18" />
					
			<widget name="key_yellow"
					position="280,360"
					size="140,40"
					valign="center"
					halign="center"
					zPosition="5"
					transparent="1"
					foregroundColor="white"
					font="Regular;18" />
					
			<widget name="key_blue"
					position="420,360"
					size="140,40"
					valign="center"
					halign="center"
					zPosition="5"
					transparent="1"
					foregroundColor="white"
					font="Regular;18" />
	
			<ePixmap name="red"
					 pixmap="skin_default/buttons/red.png"
					 position="0,360"
					 size="140,40"
					 zPosition="4"
					 transparent="1"
					 alphatest="on" />
					 
			<ePixmap name="green"
					 pixmap="skin_default/buttons/green.png"
					 position="140,360"
					 size="140,40"
					 zPosition="4"
					 transparent="1"
					 alphatest="on" />
					 
			<ePixmap name="yellow"
					 pixmap="skin_default/buttons/yellow.png"
					 position="280,360"
					 size="140,40"
					 zPosition="4"
					 transparent="1"
					 alphatest="on" />
					 
			<ePixmap name="blue"
					 pixmap="skin_default/buttons/blue.png"
					 position="420,360"
					 size="140,40"
					 zPosition="4"
					 transparent="1"
					 alphatest="on" />
		</screen>"""
	def __init__(self, session, timerinstance):
		self.session = session
		self.list = []
		self.timerinstance = timerinstance
		self.remotetimer_old = config.ipboxclient.remotetimers.value
		
		Screen.__init__(self, session)
		ConfigListScreen.__init__(self, self.list)

		if getImageDistro() in ("openatv"):
			self.setTitle(_('IPBOX Client'))
		else:
			self.setTitle(_('GBIpbox Client'))
		
		self["VKeyIcon"] = Boolean(False)
		self["text"] = StaticText(_('NOTE: the remote HDD feature require samba installed on server box.'))
		self["key_red"] = Button(_('Cancel'))
		self["key_green"] = Button(_('Save'))
		self["key_yellow"] = Button(_('Scan'))
		self["key_blue"] = Button(_('About'))
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"cancel": self.keyCancel,
			"red": self.keyCancel,
			"green": self.keySave,
			"yellow": self.keyScan,
			"blue": self.keyAbout
		}, -2)
		
		self.populateMenu()
		
		if not config.ipboxclient.firstconf.value:
			self.timer = eTimer()
			self.timer.callback.append(self.scanAsk)
			self.timer.start(100)

	def scanAsk(self):
		self.timer.stop()
		self.session.openWithCallback(self.scanConfirm, MessageBox, _("Do you want to scan for a server?"), MessageBox.TYPE_YESNO)
		
	def scanConfirm(self, confirmed):
		if confirmed:
			self.keyScan()
			
	def populateMenu(self):
		self.list = []
		self.list.append(getConfigListEntry(_("Host"), config.ipboxclient.host))
		self.list.append(getConfigListEntry(_("HTTP port"), config.ipboxclient.port))
		self.list.append(getConfigListEntry(_("Streaming port"), config.ipboxclient.streamport))
		self.list.append(getConfigListEntry(_("Authentication"), config.ipboxclient.auth))
		if config.ipboxclient.auth.value:
			self.list.append(getConfigListEntry(_("Username"), config.ipboxclient.username))
			self.list.append(getConfigListEntry(_("Password"), config.ipboxclient.password))
		self.list.append(getConfigListEntry(_("Use remote HDD"), config.ipboxclient.mounthdd))
		self.list.append(getConfigListEntry(_("Use remote timers"), config.ipboxclient.remotetimers))
		self.list.append(getConfigListEntry(_("Schedule sync"), config.ipboxclient.schedule))
		if config.ipboxclient.schedule.getValue():
			self.list.append(getConfigListEntry(_("Time of sync to start"), config.ipboxclient.scheduletime))
			self.list.append(getConfigListEntry(_("Repeat how often"), config.ipboxclient.repeattype))
		
		self["config"].list = self.list
		self["config"].l.setList(self.list)
		
	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		self.populateMenu()

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		self.populateMenu()

	def keySave(self):
		for x in self["config"].list:
			x[1].save()
		config.ipboxclient.firstconf.value = True
		config.ipboxclient.firstconf.save()
		if self.timerinstance:
			self.timerinstance.refreshScheduler()
			
		mount = GBIpboxMount(self.session)
		mount.remount()
			
		self.messagebox = self.session.open(MessageBox, _('Please wait while download is in progress.\nNOTE: If you have parental control enabled on remote box, the local settings will be overwritten.'), MessageBox.TYPE_INFO, enable_input = False)
		self.timer = eTimer()
		self.timer.callback.append(self.download)
		self.timer.start(100)
	
	def keyCancel(self):
		for x in self["config"].list:
			x[1].cancel()
		self.close()
		
	def keyAbout(self):
		self.session.open(GBIpboxAbout)
		
	def keyScan(self):
		self.messagebox = self.session.open(MessageBox, _('Please wait while scan is in progress.\nThis operation may take a while'), MessageBox.TYPE_INFO, enable_input = False)
		self.timer = eTimer()
		self.timer.callback.append(self.scan)
		self.timer.start(100)
		
	def scan(self):
		self.timer.stop()
		scanner = GBIpboxScan(self.session)
		self.scanresults = scanner.scan()
		self.messagebox.close()
		self.timer = eTimer()
		self.timer.callback.append(self.parseScanResults)
		self.timer.start(100)
		
	def parseScanResults(self):
		self.timer.stop()
		if len(self.scanresults) > 0:
			menulist = []
			for result in self.scanresults:
				menulist.append((result[0] + ' (' + result[1] + ')', result))
			menulist.append((_('Cancel'), None))
			message = _("Choose your main device")
			self.session.openWithCallback(self.scanCallback, MessageBox, message, list=menulist)
		else:
			self.session.open(MessageBox, _("No devices found"), type = MessageBox.TYPE_ERROR)
		
	def scanCallback(self, result):
		if (result):
			config.ipboxclient.host.value = result[1]
			config.ipboxclient.host.save()
			config.ipboxclient.port.value = 80
			config.ipboxclient.port.save()
			config.ipboxclient.streamport.value = 8001
			config.ipboxclient.streamport.save()
			config.ipboxclient.auth.value = False
			config.ipboxclient.auth.save()
			config.ipboxclient.firstconf.value = True
			config.ipboxclient.firstconf.save()
			
			mount = GBIpboxMount(self.session)
			mount.remount()

			self.populateMenu()
			
	def download(self):
		self.timer.stop()
		downloader = GBIpboxDownloader(self.session)
		try:
			downloader.download()
			self.messagebox.close()
			self.timer = eTimer()
			self.timer.callback.append(self.downloadCompleted)
			self.timer.start(100)
		except Exception, e:
			print e
			self.messagebox.close()
			self.timer = eTimer()
			self.timer.callback.append(self.downloadError)
			self.timer.start(100)

	def restart(self, response):
		if response:
			self.session.open(TryQuitMainloop, 3)
		else:
			self.close()
	
	def downloadCompleted(self):
		self.timer.stop()
		if self.remotetimer_old != config.ipboxclient.remotetimers.value:
			self.session.openWithCallback(self.restart, MessageBox, _("To apply new settings, you need to reboot your STB. Do you want reboot it now?"), type = MessageBox.TYPE_YESNO)
		else:
			self.session.openWithCallback(self.close, MessageBox, _("Download completed"), type = MessageBox.TYPE_INFO)
		
	def downloadError(self):
		self.timer.stop()
		self.session.open(MessageBox, _("Cannot download data. Please check your configuration"), type = MessageBox.TYPE_ERROR)
