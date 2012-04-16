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
from ..tools.plottingtool import *

try:
	from PyQt4.Qwt5 import *
	Qwt5_loaded = True
except ImportError:
	Qwt5_loaded = False 
try:
	from matplotlib import *
	import matplotlib
	matplotlib_loaded = True
except ImportError:
	matplotlib_loaded = False 

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
		
		self.verticalLayout_plot = QVBoxLayout(self.frame_for_plot)
		
		#The ploting area
		self.plotWdg = None
		#Draw the widget
		self.iface.addDockWidget(self.location, self)
		self.iface.mapCanvas().setRenderFlag(True)
		
		
	def addOptionComboboxItems(self):
		self.comboBox.addItem("Temporary polyline")
		self.comboBox.addItem("Selected polyline")
		if Qwt5_loaded:
			self.comboBox_2.addItem("Qwt5")
		if matplotlib_loaded:
			self.comboBox_2.addItem("Matplotlib")						



	def closeEvent(self, event):
		self.emit( SIGNAL( "closed(PyQt_PyObject)" ), self )
		return QDockWidget.closeEvent(self, event)


	def addPlotWidget(self, library):
		layout = self.frame_for_plot.layout()
 		while 1:
			child = layout.takeAt(0)
			if not child:
				break
			child.widget().deleteLater()
		
		
		if library == "Qwt5":
			#self.verticalLayout_plot = QVBoxLayout(self.frame_for_plot)
			self.plotWdg = PlottingTool().changePlotWidget("Qwt5", self.frame_for_plot)
			self.verticalLayout_plot.addWidget(self.plotWdg)
		if library == "Matplotlib":
			#self.verticalLayout_plot = QVBoxLayout(self.frame_for_plot)
			self.plotWdg = PlottingTool().changePlotWidget("Matplotlib", self.frame_for_plot)
			self.verticalLayout_plot.addWidget(self.plotWdg)


