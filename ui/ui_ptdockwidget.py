# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name                 : Dockable MirrorMap
Description          : Creates a dockable map canvas
Date                 : February 1, 2011 
copyright            : (C) 2011 by Giuseppe Sucameli (Faunalia)
email                : brush.tyler@gmail.com

 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

from profiletool import Ui_ProfileTool

import platform


class Ui_PTDockWidget(QDockWidget,Ui_ProfileTool):

	TITLE = "MirrorMap"

	def __init__(self, parent, iface1, mdl1):
		QDockWidget.__init__(self, parent)
		self.setAttribute(Qt.WA_DeleteOnClose)

		#self.mainWidget = MirrorMap(self, iface)
		self.location = Qt.RightDockWidgetArea
		self.iface = iface1

		self.setupUi(self)
		#self.connect(self, SIGNAL("dockLocationChanged(Qt::DockWidgetArea)"), self.setLocation)
		self.mdl = mdl1
		#self.showed = False

	def showIt(self):
		#self.setLocation( Qt.BottomDockWidgetArea )
		self.location = Qt.BottomDockWidgetArea
		minsize = self.minimumSize()
		maxsize = self.maximumSize()
		self.setMinimumSize(minsize)
		self.setMaximumSize(maxsize)
		self.iface.mapCanvas().setRenderFlag(False)
		#Print button thing
		if QT_VERSION >= 0X040100:
			self.butPDF.setEnabled(True)
		if QT_VERSION >= 0X040300:
			self.butSVG.setEnabled(True)
		#TableWiew thing
		self.tableView.setModel(self.mdl)
		self.tableView.setColumnWidth(0, 20)
		self.tableView.setColumnWidth(1, 20)
		self.tableView.setColumnWidth(2, 150)
		hh = self.tableView.horizontalHeader()
		hh.setStretchLastSection(True)
		self.tableView.setColumnHidden(4 , True)
		self.mdl.setHorizontalHeaderLabels(["","","Layer","Band"])
		self.checkBox.setEnabled(False)
		#The ploting area
		self.plotWdg = None
		#self.addQwt5PlotWidget()
		#self.addMatPlotLibWidget()
		#Draw the widget
		self.iface.addDockWidget(self.location, self)
		self.iface.mapCanvas().setRenderFlag(True)
		
		
		"""QObject.connect(self.wdg.pushButton_2, SIGNAL("clicked()"), self.addLayer)
		QObject.connect(self.wdg.pushButton, SIGNAL("clicked()"), self.removeLayer)
		QObject.connect(self.wdg.comboBox, SIGNAL("currentIndexChanged(int)"), self.selectionMethod)
		QObject.connect(self.wdg.comboBox_2, SIGNAL("currentIndexChanged(int)"), self.changePlotLibrary)"""
		
	def addOptionComboboxItems(self):
		self.comboBox.addItem("Temporary polyline")
		self.comboBox.addItem("Selected polyline")
		self.addQwt5PlotWidget()
		self.addMatPlotLibWidget()

	def closeEvent(self, event):
		self.emit( SIGNAL( "closed(PyQt_PyObject)" ), self )
		return QDockWidget.closeEvent(self, event)


	def addQwt5PlotWidget(self):
		try:
			from PyQt4.Qwt5 import QwtPlot
			from PyQt4.Qwt5 import *
			#If succeed, add in option/item box
			self.comboBox_2.addItem("Qwt5")
			#Layout things
			self.verticalLayout_plot = QVBoxLayout(self.frame_for_plot)
			self.plotWdg = QwtPlot(self.frame_for_plot)
			sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
			sizePolicy.setHorizontalStretch(0)
			sizePolicy.setVerticalStretch(0)
			sizePolicy.setHeightForWidth(self.plotWdg.sizePolicy().hasHeightForWidth())
			self.plotWdg.setSizePolicy(sizePolicy)
			self.plotWdg.setMinimumSize(QSize(0,0))
			self.plotWdg.setAutoFillBackground(False)
			#Decoration					
			self.plotWdg.setCanvasBackground(Qt.white)
			self.plotWdg.plotLayout().setAlignCanvasToScales(True)
			zoomer = QwtPlotZoomer(QwtPlot.xBottom, QwtPlot.yLeft, QwtPicker.DragSelection, QwtPicker.AlwaysOff, self.plotWdg.canvas())
			zoomer.setRubberBandPen(QPen(Qt.blue))
			if platform.system() != "Windows":
				# disable picker in Windows due to crashes
				picker = QwtPlotPicker(QwtPlot.xBottom, QwtPlot.yLeft, QwtPicker.NoSelection, QwtPlotPicker.CrossRubberBand, QwtPicker.AlwaysOn, self.plotWdg.canvas())
				picker.setTrackerPen(QPen(Qt.green))
			#self.dockwidget.qwtPlot.insertLegend(QwtLegend(), QwtPlot.BottomLegend);
			grid = Qwt.QwtPlotGrid()
			grid.setPen(QPen(QColor('grey'), 0, Qt.DotLine))
			grid.attach(self.plotWdg)
			#Display it
			self.verticalLayout_plot.addWidget(self.plotWdg)
		except:
			pass

	def addMatPlotLibWidget(self):
		try:
			from matplotlib import *
			self.comboBox_2.addItem("Matplotlib")
		except:
			pass
		
