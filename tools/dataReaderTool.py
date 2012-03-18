# -*- coding: utf-8 -*-
#-----------------------------------------------------------
#
# Profile
# Copyright (C) 2008  Borys Jurgiel
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
# with this program; if not, print to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
#---------------------------------------------------------------------

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.Qt import *
from PyQt4.Qwt5 import *
from PyQt4.QtSvg import * # required in some distros
from qgis.core import *

from math import sqrt
from profilebase import Ui_ProfileBase

import platform


class DataReaderTool:

	def dataReaderTool(self, iface1,widget1,tool1,profile1,pointstoDraw1,color1,nr1):
		self.dockwidget = widget1
		self.tool = tool1
		self.profiles = profile1
		self.pointstoDraw = pointstoDraw1
		nr = nr1
		self.iface = iface1
		if self.pointstoDraw == None: 
			return
		if self.profiles[nr]["layer"] == None: 
			return
		layer = self.profiles[nr]["layer"]

		choosenBand = self.profiles[nr]["band"]
		#Get the values on the lines
		steps = 1000  # max graph width in pixels
		l = []
		z = []
		lbefore = 0
		for i in range(0,len(self.pointstoDraw)-2):  # work for each segment of polyline
			# for each polylines, set points x,y with map crs (%D) and layer crs (%C)
			pointstoCal1 = self.tool.toLayerCoordinates(self.profiles[nr]["layer"] , QgsPoint(self.pointstoDraw[i][0],self.pointstoDraw[i][1]))
			pointstoCal2 = self.tool.toLayerCoordinates(self.profiles[nr]["layer"] , QgsPoint(self.pointstoDraw[i+1][0],self.pointstoDraw[i+1][1]))
			x1D = float(self.pointstoDraw[i][0])
			y1D = float(self.pointstoDraw[i][1])
			x2D = float(self.pointstoDraw[i+1][0])
			y2D = float(self.pointstoDraw[i+1][1])
			x1C = float(pointstoCal1.x())
			y1C = float(pointstoCal1.y())
			x2C = float(pointstoCal2.x())
			y2C = float(pointstoCal2.y())
			#lenght between (x1,y1) and (x2,y2)
			tlC = sqrt (((x2C-x1C)*(x2C-x1C)) + ((y2C-y1C)*(y2C-y1C)))
			#Set the res of calcul
			try:
				res = self.profiles[nr]["layer"].rasterUnitsPerPixel() * tlC / max(abs(x2C-x1C), abs(y2C-y1C))    # res depend on the angle of ligne with normal
			except ZeroDivisionError:
				res = layer.rasterUnitsPerPixel() * 1.2
			#enventually use bigger step
			if res != 0 and tlC/res < steps:
				steps = int(tlC/res)
			if steps < 2:
				steps = 2
			# calculate dx, dy and dl for one step
			dxD = (x2D - x1D) / steps
			dyD = (y2D - y1D) / steps
			dlD = sqrt ((dxD*dxD) + (dyD*dyD))
			dxC = (x2C - x1C) / steps
			dyC = (y2C - y1C) / steps
			#dlC = sqrt ((dxC*dxC) + (dyC*dyC))
			stepp = steps / 10
			if stepp == 0:
				stepp = 1
			progress = "Creating profile: "
			temp = 0
			# reading data
			for n in range(steps+1):
				l += [dlD * n + lbefore]
				xC = x1C + dxC * n
				yC = y1C + dyC * n
				ident = layer.identify(QgsPoint(xC,yC))
				try:
					attr = float(ident[1].values()[choosenBand])
				except:
					attr = 0
				#print "Null cell value catched as zero!"  # For none values, profile height = 0. It's not elegant...
				z += [attr]
				temp = n
				if n % stepp == 0:
					progress += "|"
					#self.iface.mainWindow().statusBar().showMessage(QString(progress))
			lbefore = l[len(l)-1]
		#End of polyline analysis
		#filling the main data dictionary "profiles"
		self.profiles[nr]["l"] = l
		self.profiles[nr]["z"] = z
		#self.iface.mainWindow().statusBar().showMessage(QString(""))
		self.profiles[nr]["curve"] = QwtPlotCurve(layer.name())
		self.profiles[nr]["curve"].setData(l, z)
		self.profiles[nr]["curve"].attach(self.dockwidget.qwtPlot)
		self.profiles[nr]["curve"].setPen(QPen(color1, 3))
		# updating everything
		#self.setColor(None)
		self.dockwidget.qwtPlot.replot()
		#self.reScalePlot(self.dockwidget.scaleSlider.value())

	def getProfileCurve(self,nr):
		return self.profiles[nr]["curve"]



