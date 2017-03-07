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
"""
from PyQt4.QtCore import *
from PyQt4.QtGui import *
"""
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *

from qgis.core import *
from qgis.gui import *
import qgis

from .selectlinetool import SelectLineTool



class ProfiletoolMapToolRenderer():

    def __init__(self, profiletool):
        self.profiletool = profiletool
        self.iface = self.profiletool.iface
        self.canvas = self.profiletool.iface.mapCanvas()
        self.tool = ProfiletoolMapTool(self.canvas,self.profiletool.plugincore.action)        #the mouselistener
        self.pointstoDraw = []  #Polyline in mapcanvas CRS analysed
        self.pointstoCal = []
        self.dblclktemp = None        #enable disctinction between leftclick and doubleclick
        self.lastFreeHandPoints = []
        
        
        self.textquit0 = "Click for polyline and double click to end (right click to cancel then quit)"
        self.textquit1 = "Select the polyline in a vector layer (Right click to quit)"
        
        self.layerindex = None                            #for selection mode
        self.previousLayer = None                        #for selection mode
    

#************************************* Mouse listener actions ***********************************************

    def moved(self,position):            #draw the polyline on the temp layer (rubberband)
        if self.profiletool.dockwidget.selectionmethod == 0:
            if len(self.pointstoDraw) > 0:
                #Get mouse coords
                mapPos = self.canvas.getCoordinateTransform().toMapCoordinates(position["x"],position["y"])
                #Draw on temp layer
                try:    #qgis2
                    if QGis.QGIS_VERSION_INT >= 10900:
                        self.profiletool.rubberband.reset(QGis.Line)
                    else:
                        self.profiletool.rubberband.reset(self.profiletool.polygon)
                except: #qgis3
                    self.profiletool.rubberband.reset(qgis.core.QgsWkbTypes.LineGeometry)
                        
                for i in range(0,len(self.pointstoDraw)):
                     self.profiletool.rubberband.addPoint(QgsPoint(self.pointstoDraw[i][0],self.pointstoDraw[i][1]))
                self.profiletool.rubberband.addPoint(QgsPoint(mapPos.x(),mapPos.y()))
        if self.profiletool.dockwidget.selectionmethod == 1:
            return



    def rightClicked(self,position):    #used to quit the current action
        if self.profiletool.dockwidget.selectionmethod == 0:
            mapPos = self.canvas.getCoordinateTransform().toMapCoordinates(position["x"],position["y"])
            newPoints = [[mapPos.x(), mapPos.y()]]
            #if newPoints == self.lastClicked: return # sometimes a strange "double click" is given
            if len(self.pointstoDraw) > 0:
                self.pointstoDraw = []
                self.pointstoCal = []
                self.profiletool.rubberband.reset(self.profiletool.polygon)
                self.profiletool.rubberbandpoint.hide()
            else:
                self.cleaning()
        if self.profiletool.dockwidget.selectionmethod == 1:
            try:
                self.previousLayer.removeSelection( False )
            except:
                self.iface.mainWindow().statusBar().showMessage("error right click")
            self.cleaning()



    def leftClicked(self,position):        #Add point to analyse
        mapPos = self.canvas.getCoordinateTransform().toMapCoordinates(position["x"],position["y"])
        newPoints = [[mapPos.x(), mapPos.y()]]
        if self.profiletool.doTracking :
            self.profiletool.rubberbandpoint.hide()
            
        if self.profiletool.dockwidget.selectionmethod == 0:
            if newPoints == self.dblclktemp:
                self.dblclktemp = None
                return
            else :
                if len(self.pointstoDraw) == 0:
                    self.profiletool.rubberband.reset(self.profiletool.polygon)
                self.pointstoDraw += newPoints
        if self.profiletool.dockwidget.selectionmethod == 1:
            result = SelectLineTool().getPointTableFromSelectedLine(self.iface, self.tool, newPoints, self.layerindex, self.previousLayer , self.pointstoDraw)
            self.pointstoDraw = result[0]
            self.layerindex = result[1]
            self.previousLayer = result[2]
            #self.profiletool.calculateProfil(self.pointstoDraw, self.mdl,self.plotlibrary, False)
            self.profiletool.calculateProfil(self.pointstoDraw, False)
            self.pointstoDraw = []
            self.iface.mainWindow().statusBar().showMessage(self.textquit1)

    def doubleClicked(self,position):
        if self.profiletool.dockwidget.selectionmethod == 0:
            #Validation of line
            mapPos = self.canvas.getCoordinateTransform().toMapCoordinates(position["x"],position["y"])
            newPoints = [[mapPos.x(), mapPos.y()]]
            self.pointstoDraw += newPoints
            #launch analyses
            self.iface.mainWindow().statusBar().showMessage(str(self.pointstoDraw))
            self.profiletool.calculateProfil(self.pointstoDraw)
            #Reset
            self.lastFreeHandPoints = self.pointstoDraw
            self.pointstoDraw = []
            #temp point to distinct leftclick and dbleclick
            self.dblclktemp = newPoints
            self.iface.mainWindow().statusBar().showMessage(self.textquit0)
        if self.profiletool.dockwidget.selectionmethod == 1:
            return
            
            
    def cleaning(self):            #used on right click
        try:
            #print str(self.previousLayer)
            self.previousLayer.removeSelection(False)
            #self.previousLayer.select(None)
        except:
            pass
        self.profiletool.rubberbandpoint.hide()
        self.canvas.setMapTool(self.profiletool.saveTool)
        self.profiletool.rubberband.reset(self.profiletool.polygon)
        self.iface.mainWindow().statusBar().showMessage( "" )
        
            
            
    def connectTool(self):
            
        self.tool.moved.connect(self.moved)
        self.tool.rightClicked.connect(self.rightClicked)
        self.tool.leftClicked.connect(self.leftClicked)
        self.tool.doubleClicked.connect(self.doubleClicked)
        self.tool.desactivate.connect(self.deactivate)


    def deactivate(self):        #enable clean exit of the plugin
            
        self.tool.moved.disconnect(self.moved)
        self.tool.rightClicked.disconnect(self.rightClicked)
        self.tool.leftClicked.disconnect(self.leftClicked)
        self.tool.doubleClicked.disconnect(self.doubleClicked)
        self.tool.desactivate.disconnect(self.deactivate)
        self.profiletool.rubberbandpoint.hide()
        self.profiletool.rubberband.reset(self.profiletool.polygon)
        
        self.iface.mainWindow().statusBar().showMessage("")




class ProfiletoolMapTool(QgsMapTool):

    moved = QtCore.pyqtSignal(dict)
    rightClicked = QtCore.pyqtSignal(dict)
    leftClicked = QtCore.pyqtSignal(dict)
    doubleClicked = QtCore.pyqtSignal(dict)
    desactivate = QtCore.pyqtSignal()

    def __init__(self, canvas,button):
        QgsMapTool.__init__(self,canvas)
        self.canvas = canvas
        self.cursor = QCursor(Qt.CrossCursor)
        self.button = button

    def canvasMoveEvent(self,event):
        self.moved.emit({'x': event.pos().x(), 'y': event.pos().y()})


    def canvasReleaseEvent(self,event):
        if event.button() == Qt.RightButton:
            self.rightClicked.emit({'x': event.pos().x(), 'y': event.pos().y()})
        else:
            self.leftClicked.emit( {'x': event.pos().x(), 'y': event.pos().y()} )

    def canvasDoubleClickEvent(self,event):
        self.doubleClicked.emit( {'x': event.pos().x(), 'y': event.pos().y()} )

    def activate(self):
        QgsMapTool.activate(self)
        self.canvas.setCursor(self.cursor)
        self.button.setCheckable(True)
        self.button.setChecked(True)


    def deactivate(self):
        self.desactivate.emit()
        self.button.setCheckable(False)
        QgsMapTool.deactivate(self)


    def isZoomTool(self):
        return False

    def setCursor(self,cursor):
        self.cursor = QCursor(cursor)
