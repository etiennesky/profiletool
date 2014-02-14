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
from PyQt4.QtSvg import *
import platform
from math import sqrt

has_qwt = False
has_mpl = False
try:
	from PyQt4.Qwt5 import *
	#print("profiletool : Qwt5 imported")
        has_qwt = True
except:
	pass
try:
	from matplotlib import *
        import matplotlib
	#print("profiletool : matplotlib %s imported" % matplotlib.__version__)
        has_mpl = True
except:
	pass



class PlottingTool:


	def changePlotWidget(self, library, frame_for_plot):
                #print("profiletool : changePlotWidget( %s )" % library )
		if library == "Qwt5" and has_qwt:
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
		elif library == "Matplotlib" and has_mpl:
			from matplotlib.figure import Figure
			from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg

			fig = Figure( (1.0, 1.0), linewidth=0.0, subplotpars = matplotlib.figure.SubplotParams(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)	)

			font = {'family' : 'arial', 'weight' : 'normal', 'size'   : 12}
			rc('font', **font)

			rect = fig.patch
			rect.set_facecolor((0.9,0.9,0.9))

			self.subplot = fig.add_axes((0.05, 0.15, 0.92,0.82))
			self.subplot.set_xbound(0,1000)
			self.subplot.set_ybound(0,1000)
			self.manageMatplotlibAxe(self.subplot)
			canvas = FigureCanvasQTAgg(fig)
			sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
			sizePolicy.setHorizontalStretch(0)
			sizePolicy.setVerticalStretch(0)
			canvas.setSizePolicy(sizePolicy)
			return canvas


	def drawVertLine(self,wdg, pointstoDraw, library):
		if library == "Qwt5" and has_qwt:
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
		elif library == "Matplotlib" and has_mpl:
			profileLen = 0
			for i in range(0, len(pointstoDraw)-1):
				x1 = float(pointstoDraw[i][0])
				y1 = float(pointstoDraw[i][1])
				x2 = float(pointstoDraw[i+1][0])
				y2 = float(pointstoDraw[i+1][1])
				profileLen = sqrt (((x2-x1)*(x2-x1)) + ((y2-y1)*(y2-y1))) + profileLen
				wdg.plotWdg.figure.get_axes()[0].vlines(profileLen, 0, 1000, linewidth = 1)
			profileLen = 0



	def attachCurves(self, wdg, profiles, model1, library):
		if library == "Qwt5" and has_qwt:
			for i in range(0 , model1.rowCount()):
				tmp_name = ("%s#%d") % (profiles[i]["layer"].name(), profiles[i]["band"]+1)
				curve = QwtPlotCurve(tmp_name)
				# stupid fix for #9002 - qwt setData() does not accept any values as None and using NaN does not work either.
				# so simple solution is to set all None as 0
				for j in range(0, len(profiles[i]["z"])):
					if profiles[i]["z"][j] is None:
						profiles[i]["z"][j] = 0
				curve.setData(profiles[i]["l"], profiles[i]["z"])
				curve.setPen(QPen(model1.item(i,1).data(Qt.BackgroundRole), 3))
				curve.attach(wdg.plotWdg)
				if model1.item(i,0).data(Qt.CheckStateRole):
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
		elif library == "Matplotlib" and has_mpl:
			for i in range(0 , model1.rowCount()):

				tmp_name = ("%s#%d") % (profiles[i]["layer"].name(), profiles[i]["band"]+1)
				if model1.item(i,0).data(Qt.CheckStateRole):
					wdg.plotWdg.figure.get_axes()[0].plot(profiles[i]["l"], profiles[i]["z"], gid = tmp_name, linewidth = 3, visible = True)
				else:
					wdg.plotWdg.figure.get_axes()[0].plot(profiles[i]["l"], profiles[i]["z"], gid = tmp_name, linewidth = 3, visible = False)
				self.changeColor(wdg, "Matplotlib", model1.item(i,1).data(Qt.BackgroundRole), tmp_name)
				try:
					self.reScalePlot(self.dockwidget.scaleSlider.value())
					wdg.plotWdg.figure.get_axes()[0].set_xbound( 0, max(self.profiles[len(self.profiles) - 1]["l"]) )
				except:
					pass
					#self.iface.mainWindow().statusBar().showMessage("Problem with setting scale of plotting")
			wdg.plotWdg.figure.get_axes()[0].redraw_in_frame()
			wdg.plotWdg.draw()


	def findMin(self,profiles, nr,scale):
		minVal = min( z for z in profiles[nr]["z"] if z is not None )
		maxVal = max( profiles[nr]["z"] )
		d = ( maxVal - minVal ) or 1
		margin = d * ( 105 - scale ) / 50.0
		return minVal - margin


	def findMax(self,profiles, nr,scale):
		minVal = min( z for z in profiles[nr]["z"] if z is not None )
		maxVal = max( profiles[nr]["z"] )
		d = ( maxVal - minVal ) or 1
		margin = d * ( 105 - scale ) / 50.0
		return maxVal + margin


	def reScalePlot(self,scale, wdg, profiles, library): 						# called when scale slider moved
		if profiles == None:
			return
		else:
			minimumValue = 1000000000
			maximumValue = -1000000000
			for i in range(0,len(profiles)):
				if profiles[i]["layer"] != None and len([z for z in profiles[i]["z"] if z is not None]) > 0:
					if self.findMin(profiles, i,scale) < minimumValue:
						minimumValue = self.findMin(profiles, i,scale)
					if self.findMax(profiles, i,scale) > maximumValue:
						maximumValue = self.findMax(profiles, i,scale)
			if minimumValue < maximumValue:
				if library == "Qwt5" and has_qwt:
					wdg.plotWdg.setAxisScale(0,minimumValue,maximumValue,0)
					wdg.plotWdg.replot()
				elif library == "Matplotlib" and has_mpl:
					wdg.plotWdg.figure.get_axes()[0].set_ybound(minimumValue,maximumValue)
					wdg.plotWdg.figure.get_axes()[0].redraw_in_frame()
					wdg.plotWdg.draw()
					pass


	def clearData(self, wdg, profiles, library): 							# erase one of profiles
		if library == "Qwt5" and has_qwt:
			wdg.plotWdg.clear()
			for i in range(0,len(self.profiles)):
				self.profiles[i]["l"] = []
				self.profiles[i]["z"] = []
			temp1 = wdg.plotWdg.itemList()
			for j in range(len(temp1)):
				if temp1[j].rtti() == QwtPlotItem.Rtti_PlotCurve:
					temp1[j].detach()
			#wdg.plotWdg.replot()
		elif library == "Matplotlib" and has_mpl:
			wdg.plotWdg.figure.get_axes()[0].cla()
			self.manageMatplotlibAxe(wdg.plotWdg.figure.get_axes()[0])
			#wdg.plotWdg.figure.get_axes()[0].redraw_in_frame()
			#wdg.plotWdg.draw()



	def changeColor(self,wdg, library, color1, name):					#Action when clicking the tableview - color
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
					temp1[i].set_color((color1.red() / 255.0 , color1.green() / 255.0 , color1.blue() / 255.0 ,  color1.alpha() / 255.0 ))
					#wdg.plotWdg.figure.get_axes()[0].redraw_in_frame()
					wdg.plotWdg.draw()
					break

			pass #why is this here?


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
			temp1 = wdg.plotWdg.figure.get_axes()[0].get_lines()
			for i in range(len(temp1)):
				if name == str(temp1[i].get_gid()):
					if bool:
						temp1[i].set_visible(True)
					else:
						temp1[i].set_visible(False)
					wdg.plotWdg.figure.get_axes()[0].redraw_in_frame()
					wdg.plotWdg.draw()
					break


	def manageMatplotlibAxe(self, axe1):
		axe1.grid()
		axe1.tick_params(axis = "both", which = "major", direction= "out", length=10, width=1, bottom = True, top = False, left = True, right = False)
		axe1.minorticks_on()
		axe1.tick_params(axis = "both", which = "minor", direction= "out", length=5, width=1, bottom = True, top = False, left = True, right = False)


	def outPrint(self, iface, wdg, mdl, library): # Postscript file rendering doesn't work properly yet.
		for i in range (0,mdl.rowCount()):
			if  mdl.item(i,0).data(Qt.CheckStateRole):
				name = str(mdl.item(i,2).data(Qt.EditRole))
				#return
		fileName = QFileDialog.getSaveFileName(iface.mainWindow(), "Save As","Profile of " + name + ".ps","PostScript Format (*.ps)")
		if fileName:
			if library == "Qwt5" and has_qwt:
				printer = QPrinter()
				printer.setCreator("QGIS Profile Plugin")
				printer.setDocName("QGIS Profile")
				printer.setOutputFileName(fileName)
				printer.setColorMode(QPrinter.Color)
				printer.setOrientation(QPrinter.Portrait)
				dialog = QPrintDialog(printer)
				if dialog.exec_():
					wdg.plotWdg.print_(printer)
			elif library == "Matplotlib" and has_mpl:
				wdg.plotWdg.figure.savefig(str(fileName))


	def outPDF(self, iface, wdg, mdl, library):
		for i in range (0,mdl.rowCount()):
			if  mdl.item(i,0).data(Qt.CheckStateRole):
				name = str(mdl.item(i,2).data(Qt.EditRole))
				break
		fileName = QFileDialog.getSaveFileName(iface.mainWindow(), "Save As","Profile of " + name + ".pdf","Portable Document Format (*.pdf)")
		if fileName:
			if library == "Qwt5" and has_qwt:
				printer = QPrinter()
				printer.setCreator('QGIS Profile Plugin')
				printer.setOutputFileName(fileName)
				printer.setOutputFormat(QPrinter.PdfFormat)
				printer.setOrientation(QPrinter.Landscape)
				wdg.plotWdg.print_(printer)
			elif library == "Matplotlib" and has_mpl:
				wdg.plotWdg.figure.savefig(str(fileName))



	def outSVG(self, iface, wdg, mdl, library):
		for i in range (0,mdl.rowCount()):
			if  mdl.item(i,0).data(Qt.CheckStateRole):
				name = str(mdl.item(i,2).data(Qt.EditRole))
				#return
		fileName = QFileDialog.getSaveFileName(iface.mainWindow(), "Save As","Profile of " + name + ".svg","Scalable Vector Graphics (*.svg)")
		if fileName:
			if library == "Qwt5" and has_qwt:
				printer = QSvgGenerator()
				printer.setFileName(fileName)
				printer.setSize(QSize(800, 400))
				wdg.plotWdg.print_(printer)
			elif library == "Matplotlib" and has_mpl:
				wdg.plotWdg.figure.savefig(str(fileName))

	def outPNG(self, iface, wdg, mdl, library):
		for i in range (0,mdl.rowCount()):
			if  mdl.item(i,0).data(Qt.CheckStateRole):
				name = str(mdl.item(i,2).data(Qt.EditRole))
				#return
		fileName = QFileDialog.getSaveFileName(iface.mainWindow(), "Save As","Profile of " + name + ".png","Portable Network Graphics (*.png)")
		if fileName:
			if library == "Qwt5" and has_qwt:
				QPixmap.grabWidget(wdg.plotWdg).save(fileName, "PNG")
			elif library == "Matplotlib" and has_mpl:
				wdg.plotWdg.figure.savefig(str(fileName))
