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
from qgis.core import *

import platform
from math import sqrt


class DataReaderTool:

	"""def __init__(self):
		self.profiles = None"""

	def dataReaderTool(self, iface1,tool1, profile1, pointstoDraw1, fullresolution1):
		"""
		Return a dictionnary : {"layer" : layer read,
								"band" : band read,
								"l" : array of computed lenght,
								"z" : array of computed z
		"""
		#init
		self.tool = tool1						#needed to transform point coordinates
		self.profiles = profile1				#profile with layer and band to compute
		self.pointstoDraw = pointstoDraw1		#the polyline to compute
		self.iface = iface1						#QGis interface to show messages in status bar

		layer = self.profiles["layer"]
		choosenBand = self.profiles["band"]

		#Get the values on the lines
		l = []
		z = []
		lbefore = 0
		for i in range(0,len(self.pointstoDraw)-2):  # work for each segment of polyline

			# for each polylines, set points x,y with map crs (%D) and layer crs (%C)
			pointstoCal1 = self.tool.toLayerCoordinates(self.profiles["layer"] , QgsPoint(self.pointstoDraw[i][0],self.pointstoDraw[i][1]))
			pointstoCal2 = self.tool.toLayerCoordinates(self.profiles["layer"] , QgsPoint(self.pointstoDraw[i+1][0],self.pointstoDraw[i+1][1]))
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
			if QGis.QGIS_VERSION_INT >= 10900:
				try:
					res = min(self.profiles["layer"].rasterUnitsPerPixelX(),self.profiles["layer"].rasterUnitsPerPixelY()) * tlC / max(abs(x2C-x1C), abs(y2C-y1C))    # res depend on the angle of ligne with normal
				except ZeroDivisionError:
					res = min(self.profiles["layer"].rasterUnitsPerPixelX(),self.profiles["layer"].rasterUnitsPerPixelY()) * 1.2
			else:
				try:
					res = self.profiles["layer"].rasterUnitsPerPixel() * tlC / max(abs(x2C-x1C), abs(y2C-y1C))    # res depend on the angle of ligne with normal
				except ZeroDivisionError:
					res = layer.rasterUnitsPerPixel() * 1.2
			#enventually use bigger step, wether full res is selected or not
			steps = 1000  # max graph width in pixels
			if fullresolution1:
				steps = int(tlC/res)
			else:
				if res != 0 and tlC/res < steps:
					steps = int(tlC/res)
				else:
					steps = 1000

			if steps < 1:
				steps = 1
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
			if i == 0:
				debut = 0
			else:
				debut = 1
			for n in range(debut, steps+1):
				l += [dlD * n + lbefore]
				xC = x1C + dxC * n
				yC = y1C + dyC * n
				attr = 0
				if layer.type() == layer.PluginLayer and layer.LAYER_TYPE == 'crayfish_viewer':
					ident = layer.identify(QgsPoint(xC,yC))
					try:
						attr = float(ident[1].values()[choosenBand])
					except:
						pass
				else: #RASTER LAYERS
					# this code adapted from valuetool plugin
					ident = layer.dataProvider().identify(QgsPoint(xC,yC), QgsRaster.IdentifyFormatValue )
					#if ident is not None and ident.has_key(choosenBand+1):
					if ident is not None and (choosenBand+1 in ident.results()):
						attr = ident.results()[choosenBand+1]
						#if attr is None:
						#	attr=float("nan")
						#print(attr)
						#if layer.dataProvider().isNoDataValue ( choosenBand+1, attr ):
							#attr = 0
				#print "Null cell value catched as zero!"  # For none values, profile height = 0. It's not elegant...

				z += [attr]
				temp = n
				if n % stepp == 0:
					progress += "|"
					self.iface.mainWindow().statusBar().showMessage(progress)
			lbefore = l[len(l)-1]
		#End of polyline analysis
		#filling the main data dictionary "profiles"
		self.profiles["l"] = l
		self.profiles["z"] = z
		self.iface.mainWindow().statusBar().showMessage("")

		return self.profiles





