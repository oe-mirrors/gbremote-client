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

from Screens.MessageBox import MessageBox
from Screens.InfoBarGenerics import InfoBarTimeshift

from GBIpboxMenu import GBIpboxMenu
from GBIpboxTimer import GBIpboxTimer
from GBIpboxMount import GBIpboxMount
from GBIpboxLocale import _

import os

timerinstance = None

def GBIpboxClient(session, **kwargs):
	global timerinstance
	session.open(GBIpboxMenu, timerinstance)
	
def GBIpboxClientAutostart(reason, session=None, **kwargs):
	global timerinstance
	timerinstance = GBIpboxTimer(session)
	
	InfoBarTimeshift.ts_disabled = True
	
	mount = GBIpboxMount(session)
	mount.automount()
	
