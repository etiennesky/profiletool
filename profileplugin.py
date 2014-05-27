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
# with this progsram; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
# 
#---------------------------------------------------------------------

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *


import resources
from ui.ui_ptdockwidget import Ui_PTDockWidget
from tools.doprofile import DoProfile
from tools.ptmaptool import ProfiletoolMapTool
from tools.tableviewtool import TableViewTool
from tools.selectlinetool import SelectLineTool
from tools.plottingtool import PlottingTool
from tools.utils import isProfilable

class ProfilePlugin:

	def __init__(self, iface):
		self.iface = iface
		self.canvas = iface.mapCanvas()
		self.wdg = None
		self.tool = None
		self.lastFreeHandPoints = []


	def initGui(self):
		# create action 
		self.action = QAction(QIcon(":/plugins/profiletool/icons/profileIcon.png"), "Terrain profile", self.iface.mainWindow())
		self.action.setWhatsThis("Plots terrain profiles")
		QObject.connect(self.action, SIGNAL("triggered()"), self.run)
		self.aboutAction = QAction("About", self.iface.mainWindow())
		QObject.connect(self.aboutAction, SIGNAL("triggered()"), self.about)

		# add toolbar button and menu item
		self.iface.addToolBarIcon(self.action)
		self.iface.addPluginToMenu("&Profile Tool", self.action)
		self.iface.addPluginToMenu("&Profile Tool", self.aboutAction)
		
		#Init classe variables
		self.tool = ProfiletoolMapTool(self.iface.mapCanvas(),self.action)		#the mouselistener
		self.dockOpened = False		#remember for not reopening dock if there's already one opened
		self.pointstoDraw = None	#Polyline in mapcanvas CRS analysed
		self.dblclktemp = None		#enable disctinction between leftclick and doubleclick
		self.mdl = None				#the model whitch in are saved layers analysed caracteristics
		self.selectionmethod = 0						#The selection method defined in option
		self.saveTool = self.canvas.mapTool()			#Save the standard mapttool for restoring it at the end
		self.layerindex = None							#for selection mode
		self.previousLayer = None						#for selection mode
		self.plotlibrary = None							#The plotting library to use
		self.textquit0 = "Click for polyline and double click to end (right click to cancel then quit)"
		self.textquit1 = "Select the polyline in a vector layer (Right click to quit)"


	def unload(self):
                if not self.wdg is None:
                        self.wdg.close()
		self.iface.removeToolBarIcon(self.action)
		self.iface.removePluginMenu("&Profile Tool", self.action)
		self.iface.removePluginMenu("&Profile Tool", self.aboutAction)


	def run(self):
		# first, check posibility
		if self.checkIfOpening() == False:
			return

		#if dock not already opened, open the dock and all the necessary thing (model,doProfile...)
		if self.dockOpened == False:
			self.mdl = QStandardItemModel(0, 5)
			self.wdg = Ui_PTDockWidget(self.iface.mainWindow(), self.iface, self.mdl)
			self.wdg.showIt()
			self.doprofile = DoProfile(self.iface,self.wdg,self.tool,self)
			self.tableViewTool = TableViewTool()
			QObject.connect(self.wdg, SIGNAL( "closed(PyQt_PyObject)" ), self.cleaning2)
			QObject.connect(self.wdg.tableView,SIGNAL("clicked(QModelIndex)"), self._onClick) 
			QObject.connect(self.wdg.pushButton_2, SIGNAL("clicked()"), self.addLayer)
			QObject.connect(self.wdg.pushButton, SIGNAL("clicked()"), self.removeLayer)
			QObject.connect(self.wdg.comboBox, SIGNAL("currentIndexChanged(int)"), self.selectionMethod)
			QObject.connect(self.wdg.comboBox_2, SIGNAL("currentIndexChanged(int)"), self.changePlotLibrary)
			self.tableViewTool.layerAddedOrRemoved.connect(self.refreshPlot)
			self.wdg.addOptionComboboxItems()
			self.addLayer()	
			self.dockOpened = True
		#Listeners of mouse
		self.connectTool()
		#init the mouse listener comportement and save the classic to restore it on quit
		self.canvas.setMapTool(self.tool)
		#init the temp layer where the polyline is draw
		self.polygon = False
		self.rubberband = QgsRubberBand(self.canvas, self.polygon)
		self.rubberband.setWidth(2)
		self.rubberband.setColor(QColor(Qt.red))
		#init the table where is saved the poyline
		self.pointstoDraw = []
		self.pointstoCal = []
		self.lastClicked = [[-9999999999.9,9999999999.9]]
		# The last valid line we drew to create a free-hand profile
		self.lastFreeHandPoints = []
		#Help about what doing
		if self.selectionmethod == 0:
			self.iface.mainWindow().statusBar().showMessage(self.textquit0)
		elif self.selectionmethod == 1:
			self.iface.mainWindow().statusBar().showMessage(self.textquit1)



#************************************* Mouse listener actions ***********************************************

	def moved(self,position):			#draw the polyline on the temp layer (rubberband)
		if self.selectionmethod == 0:
			if len(self.pointstoDraw) > 0:
				#Get mouse coords
				mapPos = self.canvas.getCoordinateTransform().toMapCoordinates(position["x"],position["y"])
				#Draw on temp layer
				if QGis.QGIS_VERSION_INT >= 10900:
					self.rubberband.reset(QGis.Line)
				else:
					self.rubberband.reset(self.polygon)
				for i in range(0,len(self.pointstoDraw)):
	 				self.rubberband.addPoint(QgsPoint(self.pointstoDraw[i][0],self.pointstoDraw[i][1]))
				self.rubberband.addPoint(QgsPoint(mapPos.x(),mapPos.y()))
		if self.selectionmethod == 1:
			return



	def rightClicked(self,position):	#used to quit the current action
		if self.selectionmethod == 0:
			mapPos = self.canvas.getCoordinateTransform().toMapCoordinates(position["x"],position["y"])
			newPoints = [[mapPos.x(), mapPos.y()]]
			#if newPoints == self.lastClicked: return # sometimes a strange "double click" is given
			if len(self.pointstoDraw) > 0:
				self.pointstoDraw = []
				self.pointstoCal = []
				self.rubberband.reset(self.polygon)
			else:
				self.cleaning()
		if self.selectionmethod == 1:
			try:
				self.previousLayer.removeSelection( False )
			except:
				self.iface.mainWindow().statusBar().showMessage("error right click")
			self.cleaning()



	def leftClicked(self,position):		#Add point to analyse
		mapPos = self.canvas.getCoordinateTransform().toMapCoordinates(position["x"],position["y"])
		newPoints = [[mapPos.x(), mapPos.y()]]
		if self.selectionmethod == 0:
			if newPoints == self.dblclktemp:
				self.dblclktemp = None
				return
			else :
				if len(self.pointstoDraw) == 0:
					self.rubberband.reset(self.polygon)
				self.pointstoDraw += newPoints
		if self.selectionmethod == 1:
			result = SelectLineTool().getPointTableFromSelectedLine(self.iface, self.tool, newPoints, self.layerindex, self.previousLayer , self.pointstoDraw)
			self.pointstoDraw = result[0]
			self.layerindex = result[1]
			self.previousLayer = result[2]
			self.doprofile.calculateProfil(self.pointstoDraw, self.mdl,self.plotlibrary, False)
			self.pointstoDraw = []
			self.iface.mainWindow().statusBar().showMessage(self.textquit1)

	def doubleClicked(self,position):
		if self.selectionmethod == 0:
			#Validation of line
			mapPos = self.canvas.getCoordinateTransform().toMapCoordinates(position["x"],position["y"])
			newPoints = [[mapPos.x(), mapPos.y()]]
			self.pointstoDraw += newPoints
			#launch analyses
			self.iface.mainWindow().statusBar().showMessage(str(self.pointstoDraw))
			self.doprofile.calculateProfil(self.pointstoDraw,self.mdl, self.plotlibrary)
			#Reset
			self.lastFreeHandPoints = self.pointstoDraw
			self.pointstoDraw = []
			#temp point to distinct leftclick and dbleclick
			self.dblclktemp = newPoints
			self.iface.mainWindow().statusBar().showMessage(self.textquit0)
		if self.selectionmethod == 1:
			return

#***************************** open and quit options *******************************************
	
	def checkIfOpening(self):
		ver = str(QGis.QGIS_VERSION)
		if ver[0] == "0" and ((ver[2] != "1") or (ver[3] != "1")):		#Check qgis version
			QMessageBox.warning(self.iface.mainWindow(), "Profile tool", "Quantum GIS version detected: "+ver+"\nProfile plugin requires version at least 0.11")
			return False
		if self.iface.mapCanvas().layerCount() == 0:					#Check a layer is opened
			QMessageBox.warning(self.iface.mainWindow(), "Profile", "First open any raster layer, please")
			return False

		layer = self.iface.activeLayer()
		
		if layer == None or not isProfilable(layer) :	#Check if a raster layer is opened and selectionned
			if self.mdl == None:
				QMessageBox.warning(self.iface.mainWindow(), "Profile Tool", "Please select one raster layer")
				return False
			if self.mdl.rowCount() == 0:
				QMessageBox.warning(self.iface.mainWindow(), "Profile Tool", "Please select one raster layer")
				return False
				
		return True
	
	def connectTool(self):
		QObject.connect(self.tool, SIGNAL("moved"), self.moved)
		QObject.connect(self.tool, SIGNAL("rightClicked"), self.rightClicked)
		QObject.connect(self.tool, SIGNAL("leftClicked"), self.leftClicked)
		QObject.connect(self.tool, SIGNAL("doubleClicked"), self.doubleClicked)
		QObject.connect(self.tool, SIGNAL("deactivate"), self.deactivate)

	def deactivate(self):		#enable clean exit of the plugin
		QObject.disconnect(self.tool, SIGNAL("moved"), self.moved)
		QObject.disconnect(self.tool, SIGNAL("leftClicked"), self.leftClicked)
		QObject.disconnect(self.tool, SIGNAL("rightClicked"), self.rightClicked)
		QObject.disconnect(self.tool, SIGNAL("doubleClicked"), self.doubleClicked)
		self.rubberband.reset(self.polygon)
		self.iface.mainWindow().statusBar().showMessage("")

	def cleaning(self):			#used on right click
		try:
			#print str(self.previousLayer)
			self.previousLayer.removeSelection(False)
			#self.previousLayer.select(None)
		except:
			pass
		self.canvas.unsetMapTool(self.tool)
		self.canvas.setMapTool(self.saveTool)
		#self.rubberband.reset(self.polygon)
		self.iface.mainWindow().statusBar().showMessage( "" )

	def cleaning2(self):		#used when Dock dialog is closed
                QObject.disconnect(self.wdg.tableView,SIGNAL("clicked(QModelIndex)"), self._onClick) 
                QObject.disconnect(self.wdg.comboBox, SIGNAL("currentIndexChanged(int)"), self.selectionMethod)
                self.tableViewTool.layerAddedOrRemoved.disconnect(self.refreshPlot)
                self.mdl = None
                self.dockOpened = False
                self.cleaning()
                self.wdg = None

	#***************************** Options *******************************************

	def selectionMethod(self,item):
		if item == 0:
			self.selectionmethod = 0
			self.tool.setCursor(Qt.CrossCursor)
		elif item == 1:
			self.selectionmethod = 1
			self.tool.setCursor(Qt.PointingHandCursor)
			self.pointstoDraw = []
			self.pointstoCal = []
			self.rubberband.reset(self.polygon)
		if self.canvas.mapTool() == self.tool:
			self.canvas.setMapTool(self.tool)
			self.connectTool()
			if self.selectionmethod == 0:
				self.iface.mainWindow().statusBar().showMessage(self.textquit0)
			elif self.selectionmethod == 1:
				self.iface.mainWindow().statusBar().showMessage(self.textquit1)
				
	def changePlotLibrary(self, item):
		self.plotlibrary = self.wdg.comboBox_2.itemText(item)
		self.wdg.addPlotWidget(self.plotlibrary)

		

	#************************* tableview function ******************************************

	def addLayer(self, layer1 = None):
		if layer1 is None:
			layer1 = self.iface.activeLayer()
		self.tableViewTool.addLayer(self.iface, self.mdl, layer1)


	def _onClick(self,index1):					#action when clicking the tableview
		self.tableViewTool.onClick(self.iface, self.wdg, self.mdl, self.plotlibrary, index1)

	def removeLayer(self, index=None):
		self.tableViewTool.removeLayer(self.iface, self.mdl, index)

	def about(self):
		from ui.ui_dlgabout import DlgAbout
		DlgAbout(self.iface.mainWindow()).exec_()

	def refreshPlot(self):
		"""
			Refreshes/updates the plot without requiring the user to 
			redraw the plot line (rubberband)
		"""
		if self.selectionmethod == 0:
			if len(self.lastFreeHandPoints) > 1:
				self.doprofile.calculateProfil(self.lastFreeHandPoints, self.mdl, self.plotlibrary)
