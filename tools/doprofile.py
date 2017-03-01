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
from PyQt4.Qt import *
from PyQt4.QtSvg import * # required in some distros
"""
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.Qt import *
from qgis.PyQt.QtSvg import * # required in some distros

from qgis.core import *
from qgis.gui import *
from .plottingtool import PlottingTool

from math import sqrt
#from profilebase import Ui_ProfileBase
from .dataReaderTool import DataReaderTool
import platform
import sys
#from PyQt4.QtCore import SIGNAL,SLOT,pyqtSignature


class DoProfile(QWidget):

    def __init__(self, iface, dockwidget1 , tool1 , plugin, parent = None):
        QWidget.__init__(self, parent)
        self.profiles = None        #dictionary where is saved the plotting data {"l":[l],"z":[z], "layer":layer1, "curve":curve1}
        self.iface = iface
        self.tool = tool1
        self.dockwidget = dockwidget1
        self.pointstoDraw = None
        self.plugin = plugin
        #matplotlib canvas signal
        self.cid = None
        self.vline = None
        #init scale widgets
        self.dockwidget.sbMaxVal.setValue(0)
        self.dockwidget.sbMinVal.setValue(0)
        self.dockwidget.sbMaxVal.setEnabled(False)
        self.dockwidget.sbMinVal.setEnabled(False)
        self.dockwidget.sbMinVal.valueChanged.connect(self.reScalePlot)
        self.dockwidget.sbMaxVal.valueChanged.connect(self.reScalePlot)
        #mouse tracking
        self.doTracking = False
        self.rubberband = None


    #**************************** function part *************************************************

    # remove layers which were removed from QGIS
    def removeClosedLayers(self, model1):
        qgisLayerNames = []
        for i in range(0, self.iface.mapCanvas().layerCount()):
                qgisLayerNames.append(self.iface.mapCanvas().layer(i).name())

        for i in range(0 , model1.rowCount()):
            layerName = model1.item(i,2).data(Qt.EditRole)
            if not layerName in qgisLayerNames:
                self.plugin.removeLayer(i)
                self.removeClosedLayers(model1)
                break

    def calculateProfil(self, points1, model1, library, vertline = True):
        self.pointstoDraw = points1
        #Mouse tracking
        self.prepar_points(self.pointstoDraw)
        
        self.removeClosedLayers(model1)
        if self.pointstoDraw == None:
            return
        PlottingTool().clearData(self.dockwidget, self.profiles, library)
        self.profiles = []
        if vertline:                        #Plotting vertical lines at the node of polyline draw
            PlottingTool().drawVertLine(self.dockwidget, self.pointstoDraw, library)

        #creating the plots of profiles
        for i in range(0 , model1.rowCount()):
            self.profiles.append( {"layer": model1.item(i,4).data(Qt.EditRole) } )
            self.profiles[i]["band"] = model1.item(i,3).data(Qt.EditRole)
            self.profiles[i] = DataReaderTool().dataReaderTool(self.iface, self.tool, self.profiles[i], self.pointstoDraw, self.dockwidget.checkBox.isChecked())
        PlottingTool().attachCurves(self.dockwidget, self.profiles, model1, library)
        PlottingTool().reScalePlot(self.dockwidget, self.profiles, library)

        #*********************** TAble tab *************************************************
        try:                                                                    #Reinitializing the table tab
            self.VLayout = self.dockwidget.scrollAreaWidgetContents.layout()
            while 1:
                child = self.VLayout.takeAt(0)
                if not child:
                    break
                child.widget().deleteLater()
        except:
            self.VLayout = QVBoxLayout(self.dockwidget.scrollAreaWidgetContents)
            self.VLayout.setContentsMargins(9, -1, -1, -1)
        #Setup the table tab
        self.groupBox = []
        self.profilePushButton = []
        self.coordsPushButton = []
        self.tableView = []
        self.verticalLayout = []
        for i in range(0 , model1.rowCount()):
            self.groupBox.append( QGroupBox(self.dockwidget.scrollAreaWidgetContents) )
            sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.groupBox[i].sizePolicy().hasHeightForWidth())
            self.groupBox[i].setSizePolicy(sizePolicy)
            self.groupBox[i].setMinimumSize(QSize(0, 150))
            self.groupBox[i].setMaximumSize(QSize(16777215, 150))
            try:    #qgis2
                self.groupBox[i].setTitle(QApplication.translate("GroupBox" + str(i), self.profiles[i]["layer"].name(), None, QApplication.UnicodeUTF8))
            except: #qgis3
                self.groupBox[i].setTitle(QApplication.translate("GroupBox" + str(i), self.profiles[i]["layer"].name(), None))
            self.groupBox[i].setObjectName("groupBox" + str(i))

            self.verticalLayout.append( QVBoxLayout(self.groupBox[i]) )
            self.verticalLayout[i].setObjectName("verticalLayout")
            #The table
            self.tableView.append( QTableView(self.groupBox[i]) )
            self.tableView[i].setObjectName("tableView" + str(i))
            font = QFont("Arial", 8)
            column = len(self.profiles[i]["l"])
            self.mdl = QStandardItemModel(2, column)
            for j in range(len(self.profiles[i]["l"])):
                self.mdl.setData(self.mdl.index(0, j, QModelIndex())  ,self.profiles[i]["l"][j])
                self.mdl.setData(self.mdl.index(0, j, QModelIndex())  ,font ,Qt.FontRole)
                self.mdl.setData(self.mdl.index(1, j, QModelIndex())  ,self.profiles[i]["z"][j])
                self.mdl.setData(self.mdl.index(1, j, QModelIndex())  ,font ,Qt.FontRole)
            self.tableView[i].verticalHeader().setDefaultSectionSize(18)
            self.tableView[i].horizontalHeader().setDefaultSectionSize(60)
            self.tableView[i].setModel(self.mdl)
            self.verticalLayout[i].addWidget(self.tableView[i])

            self.horizontalLayout = QHBoxLayout()

            #the copy to clipboard button
            self.profilePushButton.append( QPushButton(self.groupBox[i]) )
            sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.profilePushButton[i].sizePolicy().hasHeightForWidth())
            self.profilePushButton[i].setSizePolicy(sizePolicy)
            try:    #qgis2
                self.profilePushButton[i].setText(QApplication.translate("GroupBox", "Copy to clipboard", None, QApplication.UnicodeUTF8))
            except: #qgis3
                self.profilePushButton[i].setText(QApplication.translate("GroupBox", "Copy to clipboard", None))
            self.profilePushButton[i].setObjectName(str(i))
            self.horizontalLayout.addWidget(self.profilePushButton[i])

            #button to copy to clipboard with coordinates
            self.coordsPushButton.append(QPushButton(self.groupBox[i]))
            sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.coordsPushButton[i].sizePolicy().hasHeightForWidth())
            self.coordsPushButton[i].setSizePolicy(sizePolicy)
            try:    #qgis2
                self.coordsPushButton[i].setText(QApplication.translate("GroupBox", "Copy to clipboard (with coordinates)", None, QApplication.UnicodeUTF8))
            except: #qgis3
                self.coordsPushButton[i].setText(QApplication.translate("GroupBox", "Copy to clipboard (with coordinates)", None))
                
            self.coordsPushButton[i].setObjectName(str(i))
            self.horizontalLayout.addWidget(self.coordsPushButton[i])

            self.horizontalLayout.addStretch(0)
            self.verticalLayout[i].addLayout(self.horizontalLayout)

            self.VLayout.addWidget(self.groupBox[i])
            """
            QObject.connect(self.profilePushButton[i], SIGNAL("clicked()"), self.copyTable)
            QObject.connect(self.coordsPushButton[i], SIGNAL("clicked()"), self.copyTableAndCoords)
            """
            self.profilePushButton[i].clicked.connect(self.copyTable)
            self.coordsPushButton[i].clicked.connect(self.copyTableAndCoords)
            
            
            #Mouse tracking
            if self.doTracking:
                self.rubberband.show()

    def copyTable(self):                            #Writing the table to clipboard in excel form
        nr = int( self.sender().objectName() )
        self.clipboard = QApplication.clipboard()
        text = ""
        for i in range( len(self.profiles[nr]["l"]) ):
            text += str(self.profiles[nr]["l"][i]) + "\t" + str(self.profiles[nr]["z"][i]) + "\n"
        self.clipboard.setText(text)

    def copyTableAndCoords(self):                    #Writing the table with coordinates to clipboard in excel form
        nr = int( self.sender().objectName() )
        self.clipboard = QApplication.clipboard()
        text = ""
        for i in range( len(self.profiles[nr]["l"]) ):
            text += str(self.profiles[nr]["l"][i]) + "\t" + str(self.profiles[nr]["x"][i]) + "\t"\
                 + str(self.profiles[nr]["y"][i]) + "\t" + str(self.profiles[nr]["z"][i]) + "\n"
        self.clipboard.setText(text)


    def reScalePlot(self, param):                         # called when a spinbox value changed
        if type(param) != int:
            # don't execute it twice, for both valueChanged(int) and valueChanged(str) signals
            return
        if self.dockwidget.sbMinVal.value() == self.dockwidget.sbMaxVal.value() == 0:
            # don't execute it on init
            return
        PlottingTool().reScalePlot(self.dockwidget, self.profiles, self.dockwidget.cboLibrary.currentText () )


    def getProfileCurve(self,nr):
        try:
            return self.profiles[nr]["curve"]
        except:
            return None
            
            
    def activateMouseTracking(self,int1):
        if int1 == 2 :
            self.doTracking = True
            self.loadRubber()
            self.cid = self.dockwidget.plotWdg.mpl_connect('motion_notify_event', self.mouseevent_mpl)
        elif int1 == 0 :
            self.doTracking = False
            self.dockwidget.plotWdg.mpl_disconnect(self.cid)
            if self.rubberband:
                self.iface.mapCanvas().scene().removeItem(self.rubberband)
            try:
                if self.vline:
                    self.dockwidget.plotWdg.figure.get_axes()[0].lines.remove(self.vline)
                    self.dockwidget.plotWdg.draw()
            except Exception as e:
                print(str(e) )
        

    def mouseevent_mpl(self,event):
        if event.xdata:
            try:
                if self.vline:
                    self.dockwidget.plotWdg.figure.get_axes()[0].lines.remove(self.vline)
            except Exception as e:
                pass
            xdata = float(event.xdata)
            self.vline = self.dockwidget.plotWdg.figure.get_axes()[0].axvline(xdata,linewidth=2, color = 'k')
            self.dockwidget.plotWdg.draw()
            i=1
            while  i < len(self.tabmouseevent) and xdata > self.tabmouseevent[i][0] :
                i=i+1
            i=i-1
            x = self.tabmouseevent[i][1] +(self.tabmouseevent[i+1][1] - self.tabmouseevent[i][1] )/ ( self.tabmouseevent[i+1][0] - self.tabmouseevent[i][0]  )  *   (xdata - self.tabmouseevent[i][0])
            y = self.tabmouseevent[i][2] +(self.tabmouseevent[i+1][2] - self.tabmouseevent[i][2] )/ ( self.tabmouseevent[i+1][0] - self.tabmouseevent[i][0]  )  *   (xdata - self.tabmouseevent[i][0]) 
            self.rubberband.show() 
            point = QgsPoint( x,y    )
            point = QgsPoint( x,y    )
            self.rubberband.setCenter(point)
        
    def loadRubber(self):
        self.rubberband = QgsVertexMarker(self.iface.mapCanvas())
        self.rubberband.setIconSize(5)
        self.rubberband.setIconType(QgsVertexMarker.ICON_BOX) # or ICON_CROSS, ICON_X
        self.rubberband.setPenWidth(3)
            
            
    def prepar_points(self,points1):
        self.tabmouseevent=[]
        len = 0
        for i,point in enumerate(points1):
            if i==0:
                self.tabmouseevent.append([0,point[0],point[1]])
            else:
                len = len + ( (points1[i][0] - points1[i-1][0] )**2 + (points1[i][1] - points1[i-1][1])**2 )**(0.5)
                self.tabmouseevent.append([float(len) ,float(point[0]),float(point[1])])
        self.tabmouseevent = self.tabmouseevent[:-1]