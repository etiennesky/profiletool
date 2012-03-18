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
from dataReaderTool import *
import platform


class DoProfile:

	def __init__(self, iface, dockwidget1 , tool1):
		self.profiles = None		#dictionary where is saved the plotting data {"l":[l],"z":[z], "layer":layer1, "curve":curve1}
		self.iface = iface
		self.tool = tool1
		self.dockwidget = dockwidget1
		self.pointstoDraw = None
		#init slider
		QObject.connect(self.dockwidget.scaleSlider, SIGNAL("valueChanged(int)"), self.reScalePlot)
		self.dockwidget.scaleSlider.setMinimum(0)
		self.dockwidget.scaleSlider.setMaximum(100)
		self.dockwidget.scaleSlider.setValue(100)
		# setting up the main plotting widget
		self.dockwidget.qwtPlot.setCanvasBackground(Qt.white)
		self.dockwidget.qwtPlot.plotLayout().setAlignCanvasToScales(True)
		zoomer = QwtPlotZoomer(QwtPlot.xBottom, QwtPlot.yLeft, QwtPicker.DragSelection, QwtPicker.AlwaysOff, self.dockwidget.qwtPlot.canvas())
		zoomer.setRubberBandPen(QPen(Qt.blue))
		if platform.system() != "Windows":
    	# disable picker in Windows due to crashes
			picker = QwtPlotPicker(QwtPlot.xBottom, QwtPlot.yLeft, QwtPicker.NoSelection, QwtPlotPicker.CrossRubberBand, QwtPicker.AlwaysOn, self.dockwidget.qwtPlot.canvas())
			picker.setTrackerPen(QPen(Qt.green))
		#self.dockwidget.qwtPlot.insertLegend(QwtLegend(), QwtPlot.BottomLegend);
		#add grid to qwtplot
		grid = Qwt.QwtPlotGrid()
		grid.setPen(QPen(QColor('grey'), 0, Qt.DotLine))
		grid.attach(self.dockwidget.qwtPlot)
		#init the readertool
		self.datardrtl = DataReaderTool()

	#**************************** function part *************************************************

	def calculateProfil(self, points1, model1):
		self.pointstoDraw = points1
		
		if self.pointstoDraw == None: 
			return
		try:
			for i in range(0,len(self.profiles)):
				self.clearData(i)
		except:
			pass
		self.profiles = []

		#Plotting vertical lines at the node of polyline draw
		profileLen = 0
		for i in range(0, len(self.pointstoDraw)-1):
			x1 = float(self.pointstoDraw[i][0])
			y1 = float(self.pointstoDraw[i][1])
			x2 = float(self.pointstoDraw[i+1][0])
			y2 = float(self.pointstoDraw[i+1][1])
			profileLen = sqrt (((x2-x1)*(x2-x1)) + ((y2-y1)*(y2-y1))) + profileLen
			vertLine = QwtPlotMarker()
			vertLine.setLineStyle(QwtPlotMarker.VLine)
			vertLine.setXValue(profileLen)
			vertLine.attach(self.dockwidget.qwtPlot)
		profileLen = 0

		#creating the plots of profiles
		for i in range(0 , model1.rowCount()):
			self.profiles.append( {"layer": model1.item(i,4).data(Qt.EditRole).toPyObject() } )
			#self.profiles[i]["layer"] = model1.item(i,4).data(Qt.EditRole).toPyObject()
			self.profiles[i]["band"] = model1.item(i,3).data(Qt.EditRole).toPyObject() - 1
			self.iface.mainWindow().statusBar().showMessage(str(i) + " " + str(self.profiles[0]["layer"]))
			self.profiles[i] = self.datardrtl.dataReaderTool(self.iface, self.tool, self.profiles[i], self.pointstoDraw)
			self.profiles[i]["curve"].setPen(QPen(model1.item(i,1).data(Qt.BackgroundRole).toPyObject(), 3))
			if model1.item(i,0).data(Qt.CheckStateRole).toPyObject():
				self.profiles[i]["curve"].attach(self.dockwidget.qwtPlot)

		#scaling this
		self.dockwidget.qwtPlot.replot()
		self.reScalePlot(self.dockwidget.scaleSlider.value())



	def clearData(self, nr): 							# erase one of profiles
		self.dockwidget.qwtPlot.clear()
		self.profiles[nr]["l"] = []
		self.profiles[nr]["z"] = []
		try:
			self.profiles[nr]["curve"].detach()
		except:
			None
		self.dockwidget.qwtPlot.replot()
		self.reScalePlot(self.dockwidget.scaleSlider.value())


	def changeColor(self,color1,nr):					#Action when clicking the tableview - color
		if self.getProfileCurve(nr) == None: 
			return
		else:
			self.getProfileCurve(nr).setPen(QPen(color1, 3))
			self.dockwidget.qwtPlot.replot()



	def changeattachcurve(self,bool,nr):				#Action when clicking the tableview - checkstate
		if self.getProfileCurve(nr) == None: 
			return
		else:
			if bool:
				self.getProfileCurve(nr).attach(self.dockwidget.qwtPlot)
			else:
				self.getProfileCurve(nr).detach()
			self.dockwidget.qwtPlot.replot()


	def findMin(self,nr,scale):
		return min(self.profiles[nr]["z"]) * 97 / (200-scale)



	def findMax(self,nr,scale):
		return max(self.profiles[nr]["z"]) * (126-scale) / 25



	def reScalePlot(self,scale): # called when scale slider moved
		try:
			minimumValue = 1000000000
			maximumValue = -1000000000
			for i in range(0,len(self.profiles)):
				if self.profiles[i]["layer"] != None and len(self.profiles[i]["z"]) > 0:
					if self.findMin(i,scale) < minimumValue: 
						minimumValue = self.findMin(i,scale)
					if self.findMax(i,scale) > maximumValue: 
						maximumValue = self.findMax(i,scale)
			if minimumValue < maximumValue:
				self.dockwidget.qwtPlot.setAxisScale(0,minimumValue,maximumValue,0)
				self.dockwidget.qwtPlot.replot()
		except:
			return


	def getProfileCurve(self,nr):
		try:
			return self.profiles[nr]["curve"]
		except:
			return None

