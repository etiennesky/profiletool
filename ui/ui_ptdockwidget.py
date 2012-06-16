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
# with this program; if not, print to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
#---------------------------------------------------------------------

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

from profiletool import Ui_ProfileTool
from ..tools.plottingtool import *
#from ..profileplugin import ProfilePlugin

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
		"""#Print button thing
		if QT_VERSION >= 0X040100:
			self.butPDF.setEnabled(True)
		if QT_VERSION >= 0X040300:
			self.butSVG.setEnabled(True)"""
		#TableWiew thing
		self.tableView.setModel(self.mdl)
		self.tableView.setColumnWidth(0, 20)
		self.tableView.setColumnWidth(1, 20)
		self.tableView.setColumnWidth(2, 150)
		hh = self.tableView.horizontalHeader()
		hh.setStretchLastSection(True)
		self.tableView.setColumnHidden(4 , True)
		self.mdl.setHorizontalHeaderLabels(["","","Layer","Band"])
		#self.checkBox.setEnabled(False)
		
		self.verticalLayout_plot = QVBoxLayout(self.frame_for_plot)
		self.verticalLayout_plot.setMargin(0)
		
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
			print str(child)
			if not child:
				break
			if child.widget():
				child.widget().deleteLater()
			if child.layout():
				QObject.disconnect(self.butPrint, SIGNAL("clicked()"), self.outPrint)
				QObject.disconnect(self.butPDF, SIGNAL("clicked()"), self.outPDF)
				QObject.disconnect(self.butSVG, SIGNAL("clicked()"), self.outSVG)
				while 1:
					child1 = child.layout().takeAt(0)
					print str(child1)
					if not child1:
						break
					if child1.widget():	
						child1.widget().deleteLater()
				child.layout().deleteLater()				

		
		
		if library == "Qwt5":
			self.plotWdg = PlottingTool().changePlotWidget("Qwt5", self.frame_for_plot)
			self.verticalLayout_plot.addWidget(self.plotWdg)
			
			
			self.butPrint = QPushButton(self.frame_for_plot)
			sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
			sizePolicy.setHorizontalStretch(0)
			sizePolicy.setVerticalStretch(0)
			sizePolicy.setHeightForWidth(self.butPrint.sizePolicy().hasHeightForWidth())
			self.butPrint.setSizePolicy(sizePolicy)
			self.butPrint.setMinimumSize(QSize(10, 20))
			self.butPrint.setText(QApplication.translate("ProfileTool", "Print", None, QApplication.UnicodeUTF8))
			self.butPrint.setObjectName(("butPrint"))
			#self._26.addWidget(self.butPrint)
			self.butPDF = QPushButton(self.frame_for_plot)
			self.butPDF.setEnabled(False)
			sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
			sizePolicy.setHorizontalStretch(0)
			sizePolicy.setVerticalStretch(0)
			sizePolicy.setHeightForWidth(self.butPDF.sizePolicy().hasHeightForWidth())
			self.butPDF.setSizePolicy(sizePolicy)
			self.butPDF.setMinimumSize(QSize(10, 20))
			self.butPDF.setText(QApplication.translate("ProfileTool", "Save as PDF", None, QApplication.UnicodeUTF8))
			self.butPDF.setObjectName(("butPDF"))
			#self._26.addWidget(self.butPDF)
			self.butSVG = QPushButton(self.frame_for_plot)
			self.butSVG.setEnabled(False)
			sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
			sizePolicy.setHorizontalStretch(0)
			sizePolicy.setVerticalStretch(0)
			sizePolicy.setHeightForWidth(self.butSVG.sizePolicy().hasHeightForWidth())
			self.butSVG.setSizePolicy(sizePolicy)
			self.butSVG.setMinimumSize(QSize(10, 20))
			self.butSVG.setText(QApplication.translate("ProfileTool", "Save as SVG", None, QApplication.UnicodeUTF8))
			self.butSVG.setObjectName(("butSVG"))
			#self._26.addWidget(self.butSVG)

			self.horizontalLayout_tool = QHBoxLayout()
			self.horizontalLayout_tool.setMargin(0)
			self.verticalLayout_plot.addLayout(self.horizontalLayout_tool)
			
			self.horizontalLayout_tool.addWidget(self.butPrint)
			self.horizontalLayout_tool.addWidget(self.butPDF)
			self.horizontalLayout_tool.addWidget(self.butSVG)
			
			#Print button thing
			if QT_VERSION >= 0X040100:
				self.butPDF.setEnabled(True)
			if QT_VERSION >= 0X040300:
				self.butSVG.setEnabled(True)

			
			QObject.connect(self.butPrint, SIGNAL("clicked()"), self.outPrint)
			QObject.connect(self.butPDF, SIGNAL("clicked()"), self.outPDF)
			QObject.connect(self.butSVG, SIGNAL("clicked()"), self.outSVG)
			
			
			
			
		if library == "Matplotlib":
			self.plotWdg = PlottingTool().changePlotWidget("Matplotlib", self.frame_for_plot)
			self.verticalLayout_plot.addWidget(self.plotWdg)
			mpltoolbar = matplotlib.backends.backend_qt4agg.NavigationToolbar2QTAgg(self.plotWdg, self.frame_for_plot)
			self.verticalLayout_plot.addWidget( mpltoolbar )
			lstActions = mpltoolbar.actions()
			mpltoolbar.removeAction( lstActions[ 7 ] )
			mpltoolbar.removeAction( lstActions[ 8 ] )


	def outPrint(self): # Postscript file rendering doesn't work properly yet.
		PlottingTool().outPrint(self.iface, self, self.mdl, self.comboBox_2.currentText ())
		
	def outPDF(self):
		PlottingTool().outPDF(self.iface, self, self.mdl, self.comboBox_2.currentText ())

	def outSVG(self):
		PlottingTool().outSVG(self.iface, self, self.mdl, self.comboBox_2.currentText ())		

	def outPNG(self):
		PlottingTool().outPNG(self.iface, self, self.mdl, self.comboBox_2.currentText ())		

