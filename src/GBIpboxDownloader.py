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

from __future__ import absolute_import
from Components.config import config

from .GBIpboxLocale import _

from enigma import eEPGCache, eDVBDB

from xml.dom import minidom
import re
import os

try:
	from urllib.parse import urlencode, quote
	from urllib.request import urlopen
except ImportError:
	from urllib import urlencode, quote
	from urllib2 import urlopen

def getValueFromNode(event, key):
	tmp = event.getElementsByTagName(key)[0].firstChild
	if (tmp):
		return str(tmp.nodeValue)

	return ""


class GBIpboxDownloader:
	def __init__(self, session):
		self.session = session

	def download(self):
		baseurl = "http://"
		if config.ipboxclient.auth.value:
			baseurl += config.ipboxclient.username.value
			baseurl += ":"
			baseurl += config.ipboxclient.password.value
			baseurl += "@"

		baseurl += config.ipboxclient.host.value
		baseurl += ":"

		streamingurl = baseurl

		baseurl += str(config.ipboxclient.port.value)
		streamingurl += str(config.ipboxclient.streamport.value)

		print("[GBIpboxClient] web interface url: " + baseurl)
		print("[GBIpboxClient] streaming url: " + streamingurl)

		for stype in ["tv", "radio"]:
			print("[GBIpboxClient] download " + stype + " bouquets from " + baseurl)
			bouquets = self.downloadBouquets(baseurl, stype)
			print("[GBIpboxClient] save " + stype + " bouquets from " + streamingurl)
			self.saveBouquets(bouquets, streamingurl, '/etc/enigma2/bouquets.' + stype)

		print("[GBIpboxClient] reload bouquets")
		self.reloadBouquets()

		print("[GBIpboxClient] sync EPG")
		self.downloadEPG(baseurl)

		print("[GBIpboxClient] sync parental control")
		self.downloadParentalControl(baseurl)

		print("[GBIpboxClient] sync is done!")

	def getSetting(self, baseurl, key):
		httprequest = urlopen(baseurl + '/web/settings')
		xmldoc = minidom.parseString(httprequest.read())
		settings = xmldoc.getElementsByTagName('e2setting')
		for setting in settings:
			if getValueFromNode(setting, 'e2settingname') == key:
				return getValueFromNode(setting, 'e2settingvalue')

		return None

	def getEPGLocation(self, baseurl):
		return self.getSetting(baseurl, 'config.misc.epgcache_filename')

	def getParentalControlEnabled(self, baseurl):
		return self.getSetting(baseurl, 'config.ParentalControl.servicepinactive') == 'true'

	def getParentalControlType(self, baseurl):
		value = self.getSetting(baseurl, 'config.ParentalControl.type')
		if not value:
			value = 'blacklist'
		return value

	def getParentalControlPinState(self, baseurl):
		return self.getSetting(baseurl, 'config.ParentalControl.servicepinactive') == 'true'

	def getParentalControlPin(self, baseurl):
		value = self.getSetting(baseurl, 'config.ParentalControl.servicepin.0')
		if not value:
			value = "0000"
		return int(value)

	def downloadParentalControlBouquets(self, baseurl):
		bouquets = []
		httprequest = urlopen(baseurl + '/web/parentcontrollist')
		xmldoc = minidom.parseString(httprequest.read())
		services = xmldoc.getElementsByTagName('e2service')
		for service in services:
			bouquet = {}
			bouquet['reference'] = getValueFromNode(service, 'e2servicereference')
			bouquet['name'] = getValueFromNode(service, 'e2servicename')

			bouquets.append(bouquet)

		return bouquets

	def downloadBouquets(self, baseurl, stype):
		bouquets = []
		httprequest = urlopen(baseurl + '/web/bouquets?stype=' + stype)
		print("[GBIpboxClient] download bouquets from " + baseurl + '/web/bouquets?stype=' + stype)
		xmldoc = minidom.parseString(httprequest.read())
		services = xmldoc.getElementsByTagName('e2service')
		for service in services:
			bouquet = {}
			bouquet['reference'] = getValueFromNode(service, 'e2servicereference')
			bouquet['name'] = getValueFromNode(service, 'e2servicename')
			bouquet['services'] = []

			httprequest = urlopen(baseurl + '/web/getservices?' + urlencode({'sRef': bouquet['reference']}) + '&hidden=1')
			xmldoc2 = minidom.parseString(httprequest.read())
			services2 = xmldoc2.getElementsByTagName('e2service')
			for service2 in services2:
				ref = ""
				tmp = getValueFromNode(service2, 'e2servicereference')
				cnt = 0
				for x in tmp:
					ref += x
					if x == ':':
						cnt += 1
					if cnt == 10:
						break

				bouquet['services'].append({
					'reference': ref,
					'name': getValueFromNode(service2, 'e2servicename')
				})

			bouquets.append(bouquet)

		return bouquets

	def saveBouquets(self, bouquets, streamingurl, destinationfile):
		bouquetsfile = open(destinationfile, "w")
		bouquetsfile.write("#NAME Bouquets (TV)" + "\n")
		print("[GBIpboxClient] streamurl " + streamingurl)
		for bouquet in bouquets:
			pattern = r'"([A-Za-z0-9_\./\\-]*)"'
			m = re.search(pattern, bouquet['reference'])
			if not m:
				continue

			filename = m.group().strip("\"")
			bouquetsfile.write("#SERVICE " + bouquet['reference'] + "\n")
			outfile = open("/etc/enigma2/" + filename, "w")
			outfile.write("#NAME " + bouquet['name'] + "\n")
			for service in bouquet['services']:
				tmp = service['reference'].split(':')
				isDVB = False
				isStreaming = False
				url = ""

				if len(tmp) > 1 and tmp[0] == '1' and tmp[1] == '0':
					if len(tmp) > 10 and tmp[10].startswith('http%3a//'):
						isStreaming = True
					else:
						isDVB = True
						url = streamingurl + "/" + service['reference']

				if isDVB:
					outfile.write("#SERVICE " + service['reference'] + quote(url) + ":" + service['name'] + "\n")
				elif isStreaming:
					outfile.write("#SERVICE " + service['reference'] + "\n")
				else:
					outfile.write("#SERVICE " + service['reference'] + "\n")
					outfile.write("#DESCRIPTION " + service['name'] + "\n")
			outfile.close()
		bouquetsfile.close()

	def reloadBouquets(self):
		db = eDVBDB.getInstance()
		db.reloadServicelist()
		db.reloadBouquets()

	def downloadEPG(self, baseurl):
		print("[GBIpboxClient] reading remote EPG location ...")
		filename = self.getEPGLocation(baseurl)
		if not filename:
			print("[GBIpboxClient] error downloading remote EPG location. Skip EPG sync.")
			return

		print("[GBIpboxClient] remote EPG found at " + filename)

		print("[GBIpboxClient] dump remote EPG to epg.dat")
		httprequest = urlopen(baseurl + '/web/saveepg')

		httprequest = urlopen(baseurl + '/file?action=download&file=' + quote(filename))
		data = httprequest.read()
		if not data:
			print("[GBIpboxClient] cannot download remote EPG. Skip EPG sync.")
			return

		try:
			epgfile = open(config.misc.epgcache_filename.value, "w")
		except Exception:
			print("[GBIpboxClient] cannot save EPG. Skip EPG sync.")
			return

		epgfile.write(data)
		epgfile.close()

		print("[GBIpboxClient] reload EPG")
		epgcache = eEPGCache.getInstance()
		epgcache.load()

	def downloadParentalControl(self, baseurl):
		print("[GBIpboxClient] reading remote parental control status ...")

		if self.getParentalControlEnabled(baseurl):
			print("[GBIpboxClient] parental control enabled")
			config.ParentalControl.servicepinactive.value = True
			config.ParentalControl.servicepinactive.save()
			print("[GBIpboxClient] reding pin status ...")
			pinstatus = self.getParentalControlPinState(baseurl)
			pin = self.getParentalControlPin(baseurl)
			print("[GBIpboxClient] pin status is setted to " + str(pinstatus))
			config.ParentalControl.servicepinactive.value = pinstatus
			config.ParentalControl.servicepinactive.save()
			config.ParentalControl.servicepin[0].value = pin
			config.ParentalControl.servicepin[0].save()
			print("[GBIpboxClient] reading remote parental control type ...")
			stype = self.getParentalControlType(baseurl)
			print("[GBIpboxClient] parental control type is " + stype)
			config.ParentalControl.type.value = stype
			config.ParentalControl.type.save()
			print("[GBIpboxClient] download parental control services list")
			services = self.downloadParentalControlBouquets(baseurl)
			print("[GBIpboxClient] save parental control services list")
			parentalfile = open("/etc/enigma2/" + stype, "w")
			for service in services:
				parentalfile.write(service['reference'] + "\n")
			parentalfile.close()
			print("[GBIpboxClient] reload parental control")
			from Components.ParentalControl import parentalControl
			parentalControl.open()
		else:
			print("[GBIpboxClient] parental control disabled - do nothing")
