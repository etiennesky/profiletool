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
import platform
from math import sqrt
try:
	from PyQt4.Qwt5 import *
	print "Qwt5 imported"
except:
	pass
try:
	from matplotlib import *
	print "matplotlib imported"	
except:
	pass	



class PlottingTool:


	def changePlotWidget(self, library, frame_for_plot):
		if library == "Qwt5":
			plotWdg = QwtPlot(frame_for_plot)
			sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
			sizePolicy.setHorizontalStretch(0)
			sizePolicy.setVerticalStretch(0)
			sizePolicy.setHeightForWidth(plotWdg.sizePolicy().hasHeightForWidth())
			plotWdg.setSizePolicy(sizePolicy)
			plotWdg.setMinimumSize(QSize(0,0))
			plotWdg.setAutoFillBackground(False)
			#Decoration					
			plotWdg.setCanvasBackground(Qt.white)
			plotWdg.plotLayout().setAlignCanvasToScales(True)
			zoomer = QwtPlotZoomer(QwtPlot.xBottom, QwtPlot.yLeft, QwtPicker.DragSelection, QwtPicker.AlwaysOff, plotWdg.canvas())
			zoomer.setRubberBandPen(QPen(Qt.blue))
			if platform.system() != "Windows":
				# disable picker in Windows due to crashes
				picker = QwtPlotPicker(QwtPlot.xBottom, QwtPlot.yLeft, QwtPicker.NoSelection, QwtPlotPicker.CrossRubberBand, QwtPicker.AlwaysOn, plotWdg.canvas())
				picker.setTrackerPen(QPen(Qt.green))
			#self.dockwidget.qwtPlot.insertLegend(QwtLegend(), QwtPlot.BottomLegend);
			grid = Qwt.QwtPlotGrid()
			grid.setPen(QPen(QColor('grey'), 0, Qt.DotLine))
			grid.attach(plotWdg)
			return plotWdg
		if library == "Matplotlib":
			dpi = 300
			#fig = figure.Figure((1.0, 1.0), dpi=dpi)
			from matplotlib.figure import Figure
			from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
			#fig = figure.Figure((1.0, 1.0), dpi=dpi)
			fig = Figure((1.0, 1.0), dpi=dpi)			
			font = {'family' : 'arial', 'weight' : 'normal', 'size'   : 2.5}
			rc('font', **font)

			self.subplot = fig.add_subplot(1, 1, 1)
			self.subplot.set_xbound(0,1000)
			self.subplot.set_ybound(0,1000)			
			#self.subplot.grid(True, which = "both" , linewidth = 1)
			self.manageMatplotlibAxe(self.subplot)
			#return backends.backend_qt4agg.FigureCanvasQTAgg(fig)
			return FigureCanvasQTAgg(fig)


	def drawVertLine(self,wdg, pointstoDraw, library):
		if library == "Qwt5":
			profileLen = 0
			for i in range(0, len(pointstoDraw)-1):
				x1 = float(pointstoDraw[i][0])
				y1 = float(pointstoDraw[i][1])
				x2 = float(pointstoDraw[i+1][0])
				y2 = float(pointstoDraw[i+1][1])
				profileLen = sqrt (((x2-x1)*(x2-x1)) + ((y2-y1)*(y2-y1))) + profileLen
				vertLine = QwtPlotMarker()
				vertLine.setLineStyle(QwtPlotMarker.VLine)
				vertLine.setXValue(profileLen)
				vertLine.attach(wdg.plotWdg)
			profileLen = 0	
		if library == "Matplotlib":
			profileLen = 0
			for i in range(0, len(pointstoDraw)-1):
				x1 = float(pointstoDraw[i][0])
				y1 = float(pointstoDraw[i][1])
				x2 = float(pointstoDraw[i+1][0])
				y2 = float(pointstoDraw[i+1][1])
				profileLen = sqrt (((x2-x1)*(x2-x1)) + ((y2-y1)*(y2-y1))) + profileLen
				wdg.plotWdg.figure.get_axes()[0].vlines(profileLen, 0, 1000, linewidth = 0.1)
			profileLen = 0	
			#wdg.plotWdg.draw()
			#pass


	def attachCurves(self, wdg, profiles, model1, library):
		if library == "Qwt5":
			for i in range(0 , model1.rowCount()):
				curve = QwtPlotCurve(profiles[i]["layer"].name())
				curve.setData(profiles[i]["l"], profiles[i]["z"])
				curve.setPen(QPen(model1.item(i,1).data(Qt.BackgroundRole).toPyObject(), 3))
				curve.attach(wdg.plotWdg)
				if model1.item(i,0).data(Qt.CheckStateRole).toPyObject():
					curve.setVisible(True)
				else:
					curve.setVisible(False)					
				#scaling this
				try:
					wdg.setAxisScale(2,0,max(self.profiles[len(self.profiles) - 1]["l"]),0)
					self.reScalePlot(self.dockwidget.scaleSlider.value())
				except:
					pass
					#self.iface.mainWindow().statusBar().showMessage("Problem with setting scale of plotting")
			wdg.plotWdg.replot()		
		if library == "Matplotlib":
			for i in range(0 , model1.rowCount()):

				if model1.item(i,0).data(Qt.CheckStateRole).toPyObject():
					wdg.plotWdg.figure.get_axes()[0].plot(profiles[i]["l"], profiles[i]["z"], gid = profiles[i]["layer"].name(), visible = True)
				else:
					wdg.plotWdg.figure.get_axes()[0].plot(profiles[i]["l"], profiles[i]["z"], gid = profiles[i]["layer"].name(), visible = False)				
				self.changeColor(wdg, "Matplotlib", model1.item(i,1).data(Qt.BackgroundRole).toPyObject(), profiles[i]["layer"].name())
				try:
					self.reScalePlot(self.dockwidget.scaleSlider.value())
					wdg.plotWdg.figure.get_axes()[0].set_xbound( 0, max(self.profiles[len(self.profiles) - 1]["l"]) )
				except:
					pass
					#self.iface.mainWindow().statusBar().showMessage("Problem with setting scale of plotting")
			wdg.plotWdg.draw()
			
			pass
			

	def findMin(self,profiles, nr,scale):
		return min(profiles[nr]["z"]) * 97 / (200-scale)



	def findMax(self,profiles, nr,scale):
		return max(profiles[nr]["z"]) * (126-scale) / 25



	def reScalePlot(self,scale, wdg, profiles, library): 						# called when scale slider moved
		if profiles == None:
			return
		else:
			minimumValue = 1000000000
			maximumValue = -1000000000
			for i in range(0,len(profiles)):
				if profiles[i]["layer"] != None and len(profiles[i]["z"]) > 0:
					if self.findMin(profiles, i,scale) < minimumValue: 
						minimumValue = self.findMin(profiles, i,scale)
					if self.findMax(profiles, i,scale) > maximumValue: 
						maximumValue = self.findMax(profiles, i,scale)
			if minimumValue < maximumValue:
				if library == "Qwt5":
					wdg.plotWdg.setAxisScale(0,minimumValue,maximumValue,0)
					wdg.plotWdg.replot()
				if library == "Matplotlib":
					wdg.plotWdg.figure.get_axes()[0].set_ybound(minimumValue,maximumValue)
					wdg.plotWdg.draw()
					pass


	def clearData(self, wdg, profiles, library): 							# erase one of profiles
		if library == "Qwt5":
			wdg.plotWdg.clear()
			for i in range(0,len(self.profiles)):
				self.profiles[i]["l"] = []
				self.profiles[i]["z"] = []
			temp1 = wdg.plotWdg.itemList()
			for j in range(len(temp1)):
				#print str(temp1[j].rtti()) + " ** " + str(QwtPlotItem.Rtti_PlotCurve)
				if temp1[j].rtti() == QwtPlotItem.Rtti_PlotCurve:
					temp1[j].detach()
			wdg.plotWdg.replot()
		if library == "Matplotlib":
			wdg.plotWdg.figure.get_axes()[0].cla()
			self.manageMatplotlibAxe(wdg.plotWdg.figure.get_axes()[0])					
			wdg.plotWdg.draw()		


	
	def changeColor(self,wdg, library, color1 , name):					#Action when clicking the tableview - color
		if library == "Qwt5":
			temp1 = wdg.plotWdg.itemList()
			for i in range(len(temp1)):
				if name == str(temp1[i].title().text()):
					curve = temp1[i]
					curve.setPen(QPen(color1, 3))
					wdg.plotWdg.replot()
					break
		if library == "Matplotlib":
			temp1 = wdg.plotWdg.figure.get_axes()[0].get_lines()
			for i in range(len(temp1)):
				if name == str(temp1[i].get_gid()):
					temp1[i].set_color((color1.red() / 255 , color1.green() / 255 , color1.blue() / 255 ,  color1.alpha() / 255 ))
					wdg.plotWdg.draw()
					break
			
			pass


	def changeAttachCurve(self, wdg, library, bool, name):				#Action when clicking the tableview - checkstate
		if library == "Qwt5":
			temp1 = wdg.plotWdg.itemList()
			for i in range(len(temp1)):
				if name == str(temp1[i].title().text()):
					curve = temp1[i]
					if bool:
						curve.setVisible(True)
					else:
						curve.setVisible(False)
					wdg.plotWdg.replot()
					break				
		if library == "Matplotlib":
			#from matplotlib import *
			temp1 = wdg.plotWdg.figure.get_axes()[0].get_lines()
			for i in range(len(temp1)):
				#print temp1[i]
				if name == str(temp1[i].get_gid()):
					if bool:
						temp1[i].set_visible(True)
					else:
						temp1[i].set_visible(False)
					wdg.plotWdg.draw()
					break	

			
	def manageMatplotlibAxe(self, axe1):
		axe1.grid(True, which = "major" , linewidth = 0.05, linestyle = "-.")
		#axe1.grid(True, which = "major" , linestyle = ".")
		axe1.tick_params(axis = "both", which = "major", direction= "out", length=3, width=0.2)
		axe1.tick_params(axis = "both", which = "minor", direction= "out", length=1, width=0.1)


			
