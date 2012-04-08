# -*- coding: utf-8 -*-
#-----------------------------------------------------------
# 
# Profile
# Copyright (C) 2012  Patrice Verchere
#-----------------------------------------------------------
# 
# licensed under the terms of GNU GPL 2
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
# with this progsram; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
# 
#---------------------------------------------------------------------

from qgis.core import *
from qgis.gui import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *


class PlottingTool:
	
	
	def changeColor(self,wdg, library, color1 , name):					#Action when clicking the tableview - color
		if library == "Qwt5":
			from PyQt4.Qwt5 import QwtPlot
			from PyQt4.Qwt5 import *
			temp1 = wdg.plotWdg.itemList()
			for i in range(len(temp1)):
				if name == str(temp1[i].title().text()):
					curve = temp1[i]
					curve.setPen(QPen(color1, 3))
					wdg.plotWdg.replot()
					break



	def changeAttachCurve(self, wdg, library, bool, name):				#Action when clicking the tableview - checkstate
		if library == "Qwt5":
			from PyQt4.Qwt5 import QwtPlot
			from PyQt4.Qwt5 import *
			temp1 = wdg.plotWdg.itemList()
			for i in range(len(temp1)):
				if name == str(temp1[i].title().text()):
					curve = temp1[i]
					if bool:
						curve.setVisible(True)
						#curve.attach(wdg.plotWdg)
					else:
						#curve.detach()
						curve.setVisible(False)
					wdg.plotWdg.replot()
					break				

			
			
			
