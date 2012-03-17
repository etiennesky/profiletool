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


class DoProfile:

	def __init__(self, iface, dockwidget1 , tool1):
		# init variables and wigdets,3 dictionaries for profiles: 
		# {"l":[l],"z":[z], "layer":layer1, "curve":curve1} :
		self.profiles = [{"layer": None}, {"layer": None}, {"layer": None}]
		#QDialog.__init__(self)
		self.iface = iface
		#self.setupUi(self)
		self.tool = tool1
		#self.pointstoDraw = points1
		self.dockwidget = dockwidget1
		self.pointstoDraw = None
		#Listeners on dialog butons
		QObject.connect(self.dockwidget.scaleSlider, SIGNAL("valueChanged(int)"), self.reScalePlot)
		#QObject.connect(self.dockwidget.setLayer1, SIGNAL("currentIndexChanged(int)"), self.selectLayer1)
		#QObject.connect(self.dockwidget.setLayer2, SIGNAL("currentIndexChanged(int)"), self.selectLayer2)
		#QObject.connect(self.dockwidget.setLayer3, SIGNAL("currentIndexChanged(int)"), self.selectLayer3)
		##QObject.connect(self.dockwidget.setR1, SIGNAL("valueChanged(int)"), self.setColor)
		#QObject.connect(self.dockwidget.setG1, SIGNAL("valueChanged(int)"), self.setColor)
		#QObject.connect(self.dockwidget.setB1, SIGNAL("valueChanged(int)"), self.setColor)
		#QObject.connect(self.dockwidget.setR2, SIGNAL("valueChanged(int)"), self.setColor)
		#QObject.connect(self.dockwidget.setG2, SIGNAL("valueChanged(int)"), self.setColor)
		#QObject.connect(self.dockwidget.setB2, SIGNAL("valueChanged(int)"), self.setColor)
		#QObject.connect(self.dockwidget.setR3, SIGNAL("valueChanged(int)"), self.setColor)
		#QObject.connect(self.dockwidget.setG3, SIGNAL("valueChanged(int)"), self.setColor)
		#QObject.connect(self.dockwidget.setB3, SIGNAL("valueChanged(int)"), self.setColor)
		QObject.connect(self.dockwidget.butPrint, SIGNAL("clicked()"), self.outPrint)
		QObject.connect(self.dockwidget.butPDF, SIGNAL("clicked()"), self.outPDF)
		QObject.connect(self.dockwidget.butSVG, SIGNAL("clicked()"), self.outSVG)
		# buttons activity
		if QT_VERSION >= 0X040100:
			self.dockwidget.butPDF.setEnabled(True)
		if QT_VERSION >= 0X040300:
			self.dockwidget.butSVG.setEnabled(True)
		# setting up the sliders
		#self.dockwidget.setR1.setValue(100)
		#self.dockwidget.setG1.setValue(0)
		#self.dockwidget.setB1.setValue(0)
		#self.dockwidget.setR2.setValue(0)
		#self.dockwidget.setG2.setValue(100)
		#self.dockwidget.setB2.setValue(0)
		#self.dockwidget.setR3.setValue(0)
		#self.dockwidget.setG3.setValue(0)
		#self.dockwidget.setB3.setValue(100)
		self.dockwidget.scaleSlider.setMinimum(0)
		self.dockwidget.scaleSlider.setMaximum(100)
		self.dockwidget.scaleSlider.setValue(100)
		# list of usable layers, first the active one
		self.layerList=[]
		actLayer=self.iface.activeLayer()
 		self.profiles[0]["layer"] = actLayer
		self.layerList += [actLayer]
		mapCanvas = self.iface.mapCanvas()
		for i in range(mapCanvas.layerCount()):
			layer = mapCanvas.layer(i)
			if layer.type() == layer.RasterLayer:
				self.layerList += [layer]
		# filling the comboboxes
		#self.dockwidget.setLayer1.addItem(actLayer.name())
		#self.dockwidget.setLayer2.addItem("")
		#self.dockwidget.setLayer3.addItem("")
		#for i in range(1,len(self.layerList)):
			#self.dockwidget.setLayer1.addItem(self.layerList[i].name())
			#self.dockwidget.setLayer2.addItem(self.layerList[i].name())
			#self.dockwidget.setLayer3.addItem(self.layerList[i].name())
		# setting up the main plotting widget
		self.dockwidget.qwtPlot.setCanvasBackground(Qt.white)
		self.dockwidget.qwtPlot.plotLayout().setAlignCanvasToScales(True)
		zoomer = QwtPlotZoomer(QwtPlot.xBottom, QwtPlot.yLeft, QwtPicker.DragSelection, QwtPicker.AlwaysOff, self.dockwidget.qwtPlot.canvas())
		zoomer.setRubberBandPen(QPen(Qt.blue))
		if platform.system() != "Windows":
    # disable picker in Windows due to crashes
			picker = QwtPlotPicker(QwtPlot.xBottom, QwtPlot.yLeft, QwtPicker.NoSelection, QwtPlotPicker.CrossRubberBand, QwtPicker.AlwaysOn, self.dockwidget.qwtPlot.canvas())
			picker.setTrackerPen(QPen(Qt.green))
		self.dockwidget.qwtPlot.insertLegend(QwtLegend(), QwtPlot.BottomLegend);
		# general statistics label
		"""text  = "Starting point: " + str(self.pointstoDraw[0][0]) + " : "+ str(self.pointstoDraw[0][1])
		text += "\nEnding point: " + str(self.pointstoDraw[len(self.pointstoDraw)-1][0]) + " : "+ str(self.pointstoDraw[len(self.pointstoDraw)-1][1])
		#Compute de lenght with map crs and plot vert. lines on graph
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
			vertLine.attach(self.qwtPlot)
			text += "\nProfile length: "  + str(profileLen)
			self.stats.setText(text)"""

		grid = Qwt.QwtPlotGrid()
		grid.setPen(QPen(QColor('grey'), 0, Qt.DotLine))
		grid.attach(self.dockwidget.qwtPlot)


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

	def calculateProfil(self, points1, layer1):
		self.pointstoDraw = points1
		layerList = layer1
		if self.pointstoDraw == None: 
			return
		for i in range(0,len(self.profiles)):
			self.clearData(i)
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
		for i in range(0,len(layerList)):
			self.profiles.append({"layer": layerList[i][0]})
			self.profiles[i]["band"] = layerList[i][1]
			self.readData(i)
	
  
	def readData(self,nr): # read data from "layer" layer, fill the "l" and "z" lists and create "curve" QwtPlotCurve
		if self.pointstoDraw == None: 
			return
		if self.profiles[nr]["layer"] == None: 
			return
		layer = self.profiles[nr]["layer"]
		#Ask for band if more than 1
		"""if layer.bandCount() != 1:
			listband = []
			for i in range(0,layer.bandCount()):
				listband.append(str(i+1))
			testqt, ok = QInputDialog.getItem(self.iface.mainWindow(), "Band selector", "Choose the band", listband, False)
			if ok :
				choosenBand = int(testqt) - 1
			else:
				return 2
		else:
			choosenBand = 0"""
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
					self.iface.mainWindow().statusBar().showMessage(QString(progress))
			lbefore = l[len(l)-1]
		#End of polyline analysis
		#filling the main data dictionary "profiles"
		self.profiles[nr]["l"] = l
		self.profiles[nr]["z"] = z
		self.iface.mainWindow().statusBar().showMessage(QString(""))
		self.profiles[nr]["curve"] = QwtPlotCurve(layer.name())
		self.profiles[nr]["curve"].setData(l, z)
		self.profiles[nr]["curve"].attach(self.dockwidget.qwtPlot)
		# updating everything
		#self.setColor(None)
		self.dockwidget.qwtPlot.replot()
		self.reScalePlot(self.dockwidget.scaleSlider.value())
		#self.dockwidget.stat1.setText(self.stat2str(0))
		#self.dockwidget.stat2.setText(self.stat2str(1))
		#self.dockwidget.stat3.setText(self.stat2str(2))



	def stat2str(self,nr): #create statistics label
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
		return text



	def findMin(self,nr,scale):
		return min(self.profiles[nr]["z"]) * 97 / (200-scale)



	def findMax(self,nr,scale):
		return max(self.profiles[nr]["z"]) * (126-scale) / 25



	def reScalePlot(self,scale): # called when scale slider moved
		minimumValue = 1000000000
		maximumValue = -1000000000
		for i in [0,1,2]:
			if self.profiles[i]["layer"] != None and len(self.profiles[i]["z"]) > 0:
				if self.findMin(i,scale) < minimumValue: 
					minimumValue = self.findMin(i,scale)
				if self.findMax(i,scale) > maximumValue: 
					maximumValue = self.findMax(i,scale)
		if minimumValue < maximumValue:
			self.dockwidget.qwtPlot.setAxisScale(0,minimumValue,maximumValue,0)
			self.dockwidget.qwtPlot.replot()

	"""

	def selectLayer1(self,item): # called when 1st layer changed
		self.clearData(0)
		self.profiles[0]["layer"] = self.layerList[item]
		self.readData(0)



	def selectLayer2(self,item): # called when 2nd layer changed
		self.iface.mainWindow().statusBar().showMessage("2 clear")
		self.clearData(1)
		if item == 0:
			self.profiles[1]["layer"] = None
		else:
			self.profiles[1]["layer"] = self.layerList[item]
			self.iface.mainWindow().statusBar().showMessage("read data 1")
			self.readData(1)



	def selectLayer3(self,item): # called when 3th layer changed
		self.clearData(2)
		if item == 0:
			self.profiles[2]["layer"] = None
		else:
			self.profiles[2]["layer"] = self.layerList[item]
			self.readData(2)
	
	"""

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
			self.qwtPlot.print_(printer)



	def outPDF(self):
		fileName = QFileDialog.getSaveFileName(self, "Save As","Profile of " + self.profiles[0]["layer"].name() + ".pdf","Portable Document Format (*.pdf)")
		if not fileName.isEmpty():
			printer = QPrinter()
			printer.setCreator('QGIS Profile Plugin')
			printer.setOutputFileName(fileName)
			printer.setOutputFormat(QPrinter.PdfFormat)
			printer.setOrientation(QPrinter.Landscape)
			self.qwtPlot.print_(printer)



	def outSVG(self):
		fileName = QFileDialog.getSaveFileName(self, "Save As","Profile of " + self.profiles[0]["layer"].name() + ".svg","Scalable Vector Graphics (*.svg)")
		if not fileName.isEmpty():
			printer = QSvgGenerator()
			printer.setFileName(fileName)
			printer.setSize(QSize(800, 400))
			self.qwtPlot.print_(printer)

