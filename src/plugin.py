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

from Plugins.Plugin import PluginDescriptor

from Components.config import config, getConfigListEntry, ConfigSubsection, ConfigInteger, ConfigYesNo, ConfigText, ConfigClock, ConfigSelection
from Tools.Directories import fileExists
from GBIpboxClient import GBIpboxClient, GBIpboxClientAutostart
from GBIpboxRemoteTimer import GBIpboxRemoteTimer
from GBIpboxWizard import GBIpboxWizard
from GBIpboxLocale import _
from boxbranding import getImageDistro

config.ipboxclient = ConfigSubsection()
config.ipboxclient.host = ConfigText(default = "", fixed_size = False)
config.ipboxclient.port = ConfigInteger(default = 80, limits = (1, 65535))
config.ipboxclient.streamport = ConfigInteger(default = 8001, limits = (1, 65535))
config.ipboxclient.auth = ConfigYesNo(default = False)
config.ipboxclient.firstconf = ConfigYesNo(default = False)
config.ipboxclient.username = ConfigText(default = "", fixed_size = False)
config.ipboxclient.password = ConfigText(default = "", fixed_size = False)
config.ipboxclient.schedule = ConfigYesNo(default = False)
config.ipboxclient.scheduletime = ConfigClock(default = 0) # 1:00
config.ipboxclient.repeattype = ConfigSelection(default = "daily", choices = [("daily", _("Daily")), ("weekly", _("Weekly")), ("monthly", _("30 Days"))])
config.ipboxclient.mounthdd = ConfigYesNo(default = False)
config.ipboxclient.remotetimers = ConfigYesNo(default = False)

def ipboxclientRecordTimer():
	return GBIpboxRemoteTimer()

def ipboxclientStart(menuid, **kwargs):
	if getImageDistro() in ("openatv"):
		if menuid == "scan":
			return [(_("IPBOX Client"), GBIpboxClient, "ipbox_client_Start", 13)]
		else:
			return []
	elif menuid == "mainmenu":
		return [(_("GBIpboxClient"), GBIpboxClient, "ipbox_client_Start", 13)]
	else:
		return []

def getHasTuners():
	if fileExists("/proc/bus/nim_sockets"):
		nimfile = open("/proc/bus/nim_sockets")
		data = nimfile.read().strip()
		nimfile.close()
		return len(data) > 0
	return False

def Plugins(**kwargs):
	if getImageDistro() in ("openatv"):
		list = [
			PluginDescriptor(
				where = PluginDescriptor.WHERE_SESSIONSTART,
				fnc = GBIpboxClientAutostart
			),
			PluginDescriptor(
				name = "IPBOX Client",
				description = _("IPBox network client"),
				where = PluginDescriptor.WHERE_MENU,
				needsRestart = False,
				fnc = ipboxclientStart
			)
		]
	else:
		list = [
			PluginDescriptor(
				where = PluginDescriptor.WHERE_SESSIONSTART,
				fnc = GBIpboxClientAutostart
			),
			PluginDescriptor(
				name = "GBIpboxClient",
				description = _("Gigablue IPBox network client"),
				where = [PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_PLUGINMENU],
				fnc = GBIpboxClient
			),
			PluginDescriptor(
				name = "GBIpboxClient",
				description = _("Gigablue IPBox network client"),
				where = PluginDescriptor.WHERE_MENU,
				needsRestart = False,
				fnc = ipboxclientStart
			)
		]

	if config.ipboxclient.remotetimers.value:
		list.append(PluginDescriptor(
			where = PluginDescriptor.WHERE_RECORDTIMER,
			fnc = ipboxclientRecordTimer
		))

	if not config.ipboxclient.firstconf.value and getHasTuners() == False and not getImageDistro() in ("openatv"):
		list.append(PluginDescriptor(
			name = _("IPBox wizard"),
			where = PluginDescriptor.WHERE_WIZARD,
			needsRestart = False,
			fnc=(30, GBIpboxWizard)
		))
	return list
