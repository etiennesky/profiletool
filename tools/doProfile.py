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
		# init variables and wigdets,3 dictionaries for profiles: 
		# {"l":[l],"z":[z], "layer":layer1, "curve":curve1} :
		#self.profiles = [{"layer": None}, {"layer": None}, {"layer": None}]
		self.profiles = []
		self.iface = iface
		self.tool = tool1
		self.dockwidget = dockwidget1
		self.pointstoDraw = None
		#Listeners on QDock butons
		QObject.connect(self.dockwidget.scaleSlider, SIGNAL("valueChanged(int)"), self.reScalePlot)
		QObject.connect(self.dockwidget.butPrint, SIGNAL("clicked()"), self.outPrint)
		QObject.connect(self.dockwidget.butPDF, SIGNAL("clicked()"), self.outPDF)
		QObject.connect(self.dockwidget.butSVG, SIGNAL("clicked()"), self.outSVG)
		# buttons activity
		if QT_VERSION >= 0X040100:
			self.dockwidget.butPDF.setEnabled(True)
		if QT_VERSION >= 0X040300:
			self.dockwidget.butSVG.setEnabled(True)
		# setting up the slider
		self.dockwidget.scaleSlider.setMinimum(0)
		self.dockwidget.scaleSlider.setMaximum(100)
		self.dockwidget.scaleSlider.setValue(100)
		"""# list of usable layers, first the active one
		self.layerList=[]
		actLayer=self.iface.activeLayer()
 		self.profiles[0]["layer"] = actLayer
		self.layerList += [actLayer]
		mapCanvas = self.iface.mapCanvas()
		for i in range(mapCanvas.layerCount()):
			layer = mapCanvas.layer(i)
			if layer.type() == layer.RasterLayer:
				self.layerList += [layer]"""
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

		self.datardrtl = DataReaderTool()


	def clearData(self, nr): # erase one of profiles
		self.dockwidget.qwtPlot.clear()
		self.profiles[nr]["l"] = []
		self.profiles[nr]["z"] = []
		try:
			self.profiles[nr]["curve"].detach()
		except:
			None
		self.dockwidget.qwtPlot.replot()
		self.reScalePlot(self.dockwidget.scaleSlider.value())
		#self.dockwidget.stat1.setText(self.stat2str(0))
		#self.dockwidget.stat2.setText(self.stat2str(1))
		#self.dockwidget.stat3.setText(self.stat2str(2))

	def changeColor(self,color1,nr):
		if self.datardrtl.getProfileCurve(nr) == None: 
			return
		else:
			self.datardrtl.getProfileCurve(nr).setPen(QPen(color1, 3))
			self.dockwidget.qwtPlot.replot()

	def changeattachcurve(self,bool,nr):
		if self.datardrtl.getProfileCurve(nr) == None: 
			return
		else:
			if bool:
				self.datardrtl.getProfileCurve(nr).attach(self.dockwidget.qwtPlot)
			else:
				self.datardrtl.getProfileCurve(nr).detach()
			self.dockwidget.qwtPlot.replot()

	def calculateProfil(self, points1, model1):

		self.pointstoDraw = points1

		if self.pointstoDraw == None: 
			return
		for i in range(0,len(self.profiles)):
			self.clearData(i)
		self.profiles = []
		layerList = []

	

		
		for i in range(0,model1.rowCount()):
			layertemp = model1.item(i,4).data(Qt.EditRole).toPyObject()
			#self.iface.mainWindow().statusBar().showMessage(str(layertemp))
			bandtemp = model1.item(i,3).data(Qt.EditRole).toPyObject()
			bandtemp = bandtemp - 1
			color = model1.item(i,1).data(Qt.BackgroundRole).toPyObject()
			boolisprofil = model1.item(i,0).data(Qt.CheckStateRole).toPyObject()
			#self.iface.mainWindow().statusBar().showMessage("color " + str(color))
			#color1 = color1.Color()
			layerList.append([layertemp,bandtemp])


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
		#self.iface.mainWindow().statusBar().showMessage("nombre " + str(len(layerList)) )


		for i in range(0,len(layerList)):

			self.profiles.append({"layer": layerList[i][0]})
			self.profiles[i]["band"] = layerList[i][1]
			#dataReaderTool.dataReaderTool1(self.dockwidget,self.tool,self.profiles,self.pointstoDraw)
			self.datardrtl.dataReaderTool(self.iface,self.dockwidget,self.tool,self.profiles,self.pointstoDraw,color,boolisprofil,i)
			#self.readData(i)
		self.reScalePlot(self.dockwidget.scaleSlider.value())
  

	"""def stat2str(self,nr): #create statistics label
		profile = self.profiles[nr]
		if profile["layer"] == None or len(profile["z"]) < 2:
			return ""
		mean = float(sum(profile["z"])) / float(len(profile["z"]))
		stdDev = 0.0
		for i in profile["z"]:
			stdDev += (i - mean) * (i - mean)
		stdDev = sqrt(stdDev / len(profile["l"])+1)
		text  = "\nLayer:  "    + str(profile["layer"].name())
		text += "\nPixel size: "+ str(profile["layer"].rasterUnitsPerPixel())
		text += "\nMin:  "     + str(min(profile["z"]))
		text += "\nMax:  "     + str(max(profile["z"]))
		text += "\nMean:  "    + str(mean)
		text += "\nSD:  "      + str(stdDev)
		return text"""



	def findMin(self,nr,scale):
		return min(self.profiles[nr]["z"]) * 97 / (200-scale)



	def findMax(self,nr,scale):
		return max(self.profiles[nr]["z"]) * (126-scale) / 25



	def reScalePlot(self,scale): # called when scale slider moved
		minimumValue = 1000000000
		maximumValue = -1000000000
		for i in range(0,len(self.profiles)-1):
			if self.profiles[i]["layer"] != None and len(self.profiles[i]["z"]) > 0:
				if self.findMin(i,scale) < minimumValue: 
					minimumValue = self.findMin(i,scale)
				if self.findMax(i,scale) > maximumValue: 
					maximumValue = self.findMax(i,scale)
		if minimumValue < maximumValue:
			self.dockwidget.qwtPlot.setAxisScale(0,minimumValue,maximumValue,0)
			self.dockwidget.qwtPlot.replot()



	def setColor(self,ivoid): # update colors of: plot, "colorboxes" and labels
		palette = QPalette()
  
		color = QColor(self.dockwidget.setR1.value()*2.55,self.dockwidget.setG1.value()*2.55,self.dockwidget.setB1.value()*2.55,230)
		if self.profiles[0]["layer"] != None:
			self.profiles[0]["curve"].setPen(QPen(color, 3))
		palette.setBrush(QPalette.Active,QPalette.Base,QBrush(color,Qt.SolidPattern))
		self.dockwidget.colorBox1.setPalette(palette)
		palette.setBrush(QPalette.Active,QPalette.WindowText,QBrush(color,Qt.SolidPattern))
		self.dockwidget.statBox1.setPalette(palette)
		palette.setBrush(QPalette.Active,QPalette.WindowText,QBrush(QColor(0,0,0),Qt.SolidPattern))
		self.dockwidget.stat1.setPalette(palette)

		color = QColor(self.dockwidget.setR2.value()*2.55,self.dockwidget.setG2.value()*2.55,self.dockwidget.setB2.value()*2.55,200)
		if self.profiles[1]["layer"] != None:
			self.profiles[1]["curve"].setPen(QPen(color, 3))
		palette.setBrush(QPalette.Active,QPalette.Base,QBrush(color,Qt.SolidPattern))
		self.dockwidget.colorBox2.setPalette(palette)
		palette.setBrush(QPalette.Active,QPalette.WindowText,QBrush(color,Qt.SolidPattern))
		self.dockwidget.statBox2.setPalette(palette)
		palette.setBrush(QPalette.Active,QPalette.WindowText,QBrush(QColor(0,0,0),Qt.SolidPattern))
		self.dockwidget.stat2.setPalette(palette)

		color = QColor(self.dockwidget.setR3.value()*2.55,self.dockwidget.setG3.value()*2.55,self.dockwidget.setB3.value()*2.55,200)
		if self.profiles[2]["layer"] != None:
			self.profiles[2]["curve"].setPen(QPen(color, 3))
		palette.setBrush(QPalette.Active,QPalette.Base,QBrush(color,Qt.SolidPattern))
		self.dockwidget.colorBox3.setPalette(palette)
		palette.setBrush(QPalette.Active,QPalette.WindowText,QBrush(color,Qt.SolidPattern))
		self.dockwidget.statBox3.setPalette(palette)
		palette.setBrush(QPalette.Active,QPalette.WindowText,QBrush(QColor(0,0,0),Qt.SolidPattern))
		self.dockwidget.stat3.setPalette(palette)

		self.dockwidget.qwtPlot.replot()
		del palette



	def outPrint(self): # Postscript file rendering doesn't work properly yet.
		fileName = "Profile of " + self.profiles[0]["layer"].name() + ".ps"
		printer = QPrinter()
		printer.setCreator("QGIS Profile Plugin")
		printer.setDocName("QGIS Profile")
		printer.setOutputFileName(fileName)
		printer.setColorMode(QPrinter.Color)
		printer.setOrientation(QPrinter.Portrait)
		dialog = QPrintDialog(printer)
		if dialog.exec_():
			self.dockwidget.qwtPlot.print_(printer)



	def outPDF(self):
		fileName = QFileDialog.getSaveFileName(self.iface.mainWindow(), "Save As","Profile of " + self.profiles[0]["layer"].name() + ".pdf","Portable Document Format (*.pdf)")
		if not fileName.isEmpty():
			printer = QPrinter()
			printer.setCreator('QGIS Profile Plugin')
			printer.setOutputFileName(fileName)
			printer.setOutputFormat(QPrinter.PdfFormat)
			printer.setOrientation(QPrinter.Landscape)
			self.dockwidget.qwtPlot.print_(printer)



	def outSVG(self):
		fileName = QFileDialog.getSaveFileName(self.iface.mainWindow(), "Save As","Profile of " + self.profiles[0]["layer"].name() + ".svg","Scalable Vector Graphics (*.svg)")
		if not fileName.isEmpty():
			printer = QSvgGenerator()
			printer.setFileName(fileName)
			printer.setSize(QSize(800, 400))
			self.dockwidget.qwtPlot.print_(printer)

