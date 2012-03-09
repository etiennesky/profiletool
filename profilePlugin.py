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

from selectPointTool import *
#import resources
import doProfile

class profilePlugin:

 def __init__(self, iface):
  self.iface = iface
  self.canvas = iface.mapCanvas()


 def initGui(self):
  # create action 
  self.action = QAction(QIcon(":/plugins/profile/profileIcon.png"), "Terrain profile", self.iface.mainWindow())
  self.action.setWhatsThis("Plots terrain profiles")
  QObject.connect(self.action, SIGNAL("triggered()"), self.run)
  # add toolbar button and menu item
  self.iface.addToolBarIcon(self.action)
  self.iface.addPluginToMenu("&Analyses", self.action)
  self.tool = selectPointTool(self.iface.mapCanvas(),self.action)


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
  self.iface.mainWindow().statusBar().showMessage(QString("Select starting and ending point"))
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
  self.pointstoDraw += newPoints
   
 def doubleClicked(self,position):
  #Validation of line
  mapPos = self.canvas.getCoordinateTransform().toMapCoordinates(position["x"],position["y"])
  newPoints = [[mapPos.x(), mapPos.y()]]
  self.pointstoDraw += newPoints
  #launch analyses dialog
  dialoga = doProfile.Dialog(self.iface, self.pointstoDraw,self.tool)
  dialoga.exec_()
  #Reset all
  self.rubberband.reset(self.polygon)
  self.pointstoDraw = []
  self.pointstoCal = []
  self.iface.mainWindow().statusBar().showMessage(QString("Select starting and ending point"))

 def cleaning(self):
  QObject.disconnect(self.tool, SIGNAL("moved"), self.moved)
  QObject.disconnect(self.tool, SIGNAL("leftClicked"), self.leftClicked)
  QObject.disconnect(self.tool, SIGNAL("rightClicked"), self.rightClicked)
  QObject.disconnect(self.tool, SIGNAL("doubleClicked"), self.doubleClicked)
  self.canvas.setMapTool(self.saveTool)
  self.rubberband.reset(self.polygon)
  self.points = []
  self.iface.mainWindow().statusBar().showMessage(QString(""))
