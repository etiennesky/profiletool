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

#from selectPointTool import *
import resources
import tools
from tools.ui_profiletool2 import ui_ProfileTool2
from tools.doProfile import DoProfile

class profilePlugin:

	def __init__(self, iface):
		self.iface = iface
		self.canvas = iface.mapCanvas()


	def initGui(self):
		self.dockOpened = False		#remember for not reopening dock if there's already one opened
		self.layerlist = []			#layers which are analysed
		self.pointstoDraw = None	#Polyline in mapcanvas CRS analysed
		self.dblclktemp = None
		self.mdl = None
		# create action 
		self.action = QAction(QIcon(":/plugins/profiletool/icons/profileIcon.png"), "Terrain profile", self.iface.mainWindow())
		self.action.setWhatsThis("Plots terrain profiles")
		QObject.connect(self.action, SIGNAL("triggered()"), self.run)
		# add toolbar button and menu item
		self.iface.addToolBarIcon(self.action)
		self.iface.addPluginToMenu("&Analyses", self.action)
		self.tool = tools.selectPointTool.selectPointTool(self.iface.mapCanvas(),self.action)


	def unload(self):
		self.iface.removePluginMenu("&Analyses",self.action)
		self.iface.removeToolBarIcon(self.action)


	def run(self):
		# first, check posibility
		ver = str(QGis.QGIS_VERSION)
		if ver[0] == "0" and ((ver[2] != "1") or (ver[3] != "1")):
			QMessageBox.warning(self.iface.mainWindow(), "Profile", "Quantum GIS version detected: "+ver+"\nProfile plugin requires version at least 0.11")
			return 1
		if self.iface.mapCanvas().layerCount() == 0:
			QMessageBox.warning(self.iface.mainWindow(), "Profile", "First open any raster layer, please")
			return 2
		layer = self.iface.activeLayer()
		if layer == None or layer.type() != layer.RasterLayer :
			QMessageBox.warning(self.iface.mainWindow(), "Profile", "Please select one raster layer")
			#self.choosenBand = 0
			return 3
		

		#if dock not already opened, open the dock and all the necessary thong (model,doProfile...)
		if self.dockOpened == False : 
			self.dockOpened = True
			self.wdg = ui_ProfileTool2(self.iface.mainWindow(), self.iface)
			#Set size properties
			self.wdg.setLocation( Qt.BottomDockWidgetArea )
			minsize = self.wdg.minimumSize()
			maxsize = self.wdg.maximumSize()
			self.wdg.setMinimumSize(minsize)
			self.wdg.setMaximumSize(maxsize)
			position = self.wdg.getLocation()

			"""mapCanvas = self.iface.mapCanvas()
			oldSize = mapCanvas.size()
			prevFlag = mapCanvas.renderFlag()"""
			self.iface.mapCanvas().setRenderFlag(False)
			self.iface.addDockWidget(position, self.wdg)

			"""newSize = mapCanvas.size()
			if newSize != oldSize:
				# trick: update the canvas size
				mapCanvas.resize(newSize.width() - 1, newSize.height())
				mapCanvas.setRenderFlag(prevFlag)
				mapCanvas.resize(newSize)
			else:
				mapCanvas.setRenderFlag(prevFlag)"""
			QObject.connect(self.wdg, SIGNAL( "closed(PyQt_PyObject)" ), self.cleaning2)
			#init the calcul class 
			self.doprofile = DoProfile(self.iface,self.wdg,self.tool)
			self.mdl = QStandardItemModel(0, 5)
			#init the table model in tab "profile" for choosing analysed layers
			self.wdg.tableView.setModel(self.mdl)
			self.wdg.tableView.setColumnWidth(0, 16)
			self.wdg.tableView.setColumnWidth(1, 16)
			self.wdg.tableView.setColumnWidth(2, 150)
			hh = self.wdg.tableView.horizontalHeader()
			hh.setStretchLastSection(True)
			self.wdg.tableView.setColumnHidden(4 , True)
			self.mdl.setHorizontalHeaderLabels(["","","Layer","Band"])
			
			#self.wdg.tableView.stretchLastSection(True)

			#self.wdg.tableView.setItemDelegateForColumn(0,CheckBoxDelegate(self.wdg.tableView))
			#self.wdg.tableView.setItemDelegateForColumn(1,ColorChooserDelegate(self.wdg.tableView))

			self.iface.mapCanvas().setRenderFlag(True)
			#Listener add raster
			QObject.connect(self.wdg.pushButton_2, SIGNAL("clicked()"), self.addLayer)

			self.addLayer(self.iface.activeLayer())		
			



		#Listeners of mouse
		QObject.connect(self.tool, SIGNAL("moved"), self.moved)
		QObject.connect(self.tool, SIGNAL("rightClicked"), self.rightClicked)
		QObject.connect(self.tool, SIGNAL("leftClicked"), self.leftClicked)
		QObject.connect(self.tool, SIGNAL("doubleClicked"), self.doubleClicked)

		#init things
		self.saveTool = self.canvas.mapTool()
		self.canvas.setMapTool(self.tool)
		self.polygon = False
		self.rubberband = QgsRubberBand(self.canvas, self.polygon)
		#self.iface.mainWindow().statusBar().showMessage(QString("Select starting and ending point"))
		self.pointstoDraw = []
		self.pointstoCal = []
		self.lastClicked = [[-9999999999.9,9999999999.9]]


	def moved(self,position):
		if len(self.pointstoDraw) > 0:
			#Get mouse coords
			mapPos = self.canvas.getCoordinateTransform().toMapCoordinates(position["x"],position["y"])
			#Draw on temp layer
			self.rubberband.reset(self.polygon)
			for i in range(0,len(self.pointstoDraw)):
 				self.rubberband.addPoint(QgsPoint(self.pointstoDraw[i][0],self.pointstoDraw[i][1]))
			self.rubberband.addPoint(QgsPoint(mapPos.x(),mapPos.y()))



	def rightClicked(self,position):
		#user cancelled
		mapPos = self.canvas.getCoordinateTransform().toMapCoordinates(position["x"],position["y"])
		newPoints = [[mapPos.x(), mapPos.y()]]
		if newPoints == self.lastClicked: return # sometimes a strange "double click" is given
		if len(self.pointstoDraw) > 0:
			self.pointstoDraw = []
			self.pointstoCal = []
			self.rubberband.reset(self.polygon)
		else:
			self.cleaning()
			self.lastClicked = newPoints


	def leftClicked(self,position):
		#Add point to analyse
		mapPos = self.canvas.getCoordinateTransform().toMapCoordinates(position["x"],position["y"])
		newPoints = [[mapPos.x(), mapPos.y()]]
		if newPoints == self.dblclktemp:
			return
		else :
			self.pointstoDraw += newPoints
   
	def doubleClicked(self,position):
		#Validation of line
		mapPos = self.canvas.getCoordinateTransform().toMapCoordinates(position["x"],position["y"])
		newPoints = [[mapPos.x(), mapPos.y()]]
		self.pointstoDraw += newPoints
		#launch analyses dialog
		self.doprofile.calculateProfil(self.pointstoDraw,self.mdl)
		#self.wdg.setLayer1.emit( SIGNAL("currentIndexChanged(int)"),0)
		#dialoga = tools.doProfile.Dialog(self.iface, self.pointstoDraw,self.tool)
		#dialoga.exec_()
		#Reset all
		self.rubberband.reset(self.polygon)
		self.pointstoDraw = []
		#self.pointstoCal = []
		#self.iface.mainWindow().statusBar().showMessage(QString("Select starting and ending point"))
		self.dblclktemp = newPoints

	def cleaning(self):
		QObject.disconnect(self.tool, SIGNAL("moved"), self.moved)
		QObject.disconnect(self.tool, SIGNAL("leftClicked"), self.leftClicked)
		QObject.disconnect(self.tool, SIGNAL("rightClicked"), self.rightClicked)
		QObject.disconnect(self.tool, SIGNAL("doubleClicked"), self.doubleClicked)
		self.canvas.setMapTool(self.saveTool)
		self.rubberband.reset(self.polygon)
		self.points = []
		#self.iface.mainWindow().statusBar().showMessage(QString(""))


	def cleaning2(self):
		self.mdl = None
		self.dockOpened = False
		self.cleaning()

	def addLayer(self , layer1 = None):
		if layer1 == None:
			templist=[]
			tempdico=[]
			j=0
			for i in range(0,self.iface.mapCanvas().layerCount()):
				layer = self.iface.mapCanvas().layer(i)
				if layer.type() == layer.RasterLayer:
					tempdico += [{"layer": layer , "layername" : layer.name()}]
					#templist.append(layer.name())
			#self.iface.mainWindow().statusBar().showMessage(str(i) + " " + str(tempdico)+ " " + str(len(tempdico)))
			testqt, ok = QInputDialog.getItem(self.iface.mainWindow(), "Band selector", "Choose layer", [tempdico[j]["layername"] for j in range(0,len(tempdico))], False)
			if ok:
				for i in range (0,len(tempdico)):
					if tempdico[i]["layername"] == testqt:
						layer2 = tempdico[i]["layer"]
			else: return


		else : 
			layer2 = layer1


		if layer2.bandCount() != 1:
			listband = []
			for i in range(0,layer2.bandCount()):
				listband.append(str(i+1))
			testqt, ok = QInputDialog.getItem(self.iface.mainWindow(), "Band selector", "Choose the band", listband, False)
			if ok :
				choosenBand = int(testqt) - 1
			else:
				return 2
		else:
			choosenBand = 0


		row = self.mdl.rowCount()
		self.mdl.insertRow(row)
		self.mdl.setData( self.mdl.index(row, 0, QModelIndex())  ,QVariant(True))
		self.mdl.setData( self.mdl.index(row, 1, QModelIndex())  ,QVariant(True))
		self.mdl.setData( self.mdl.index(row, 2, QModelIndex())  ,QVariant(layer2.name()))
		self.mdl.setData( self.mdl.index(row, 3, QModelIndex())  ,QVariant(choosenBand + 1))
		self.mdl.setData( self.mdl.index(row, 4, QModelIndex())  ,layer2)


