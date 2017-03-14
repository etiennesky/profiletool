# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PointProjectionDockWidget
                                 A QGIS plugin
 test
                             -------------------
        begin                : 2016-03-16
        git sha              : $Format:%H$
        copyright            : (C) 2016 by toto
        email                : toto@toto
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

import os
#PyQT libs
from PyQt4 import QtGui, uic
from PyQt4.QtCore import pyqtSignal
#Qgis libs
from qgis.core import *
from qgis.gui import *
from qgis.utils import *
#Matplotlib libs
from matplotlib import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
try:
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
except :
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
#plugin libs
from ..libs.pointprojector import *

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'pointprojection_dockwidget_base.ui'))


class PointProjectionDockWidget(QtGui.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(PointProjectionDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.pointprojector = None                                  #the class that process projection
        self.iface = iface
        self.activelayer = None                                     #the active layer (line vector layer)
        self.mapcanvas = self.iface.mapCanvas()
        self.rubberband = QgsRubberBand(self.mapcanvas, QGis.Line)  #the rubberband
        self.rubberband.setWidth(2)
        self.rubberband.setColor(QColor(Qt.red))
        #Update layer in combobox
        self.updateLayers()
        #Connectors
        self.pushButton_testline.clicked.connect(self.testLine)
        self.pushButton_extract.clicked.connect(self.extractPoints)
        self.checkBox_interpfield.stateChanged.connect(self.activePointFields)
        #self.pretelemac.iface.mapCanvas().layersChanged.connect(self.layerChanged)
        #figure matplotlib
        self.figure1 = plt.figure(0)
        font = {'family' : 'arial', 'weight' : 'normal', 'size'   : 12}
        rc('font', **font)
        self.canvas1 = FigureCanvas(self.figure1)
        self.ax = self.figure1.add_subplot(111)
        layout = QtGui.QVBoxLayout()
        try:
            self.toolbar = NavigationToolbar(self.canvas1, self.frame_mpl,True)
            layout.addWidget(self.toolbar)
        except Exception, e:
            pass
        layout.addWidget(self.canvas1)
        self.canvas1.draw()
        self.frame_mpl.setLayout(layout)
        
    def testLine(self):
        """
        Action when Test button is clicked
        """
        #reinit things
        try:
            self.activelayer.selectionChanged.disconnect(self.activeLayerSelectionChanged)
        except Exception, e:
            pass
        self.activelayer = iface.activeLayer()
        self.activelayer.selectionChanged.connect(self.activeLayerSelectionChanged)
        #create pointprojector class
        layer = self.getLayerByName(self.comboBox.currentText() )
        self.pointprojector = pointProjector(self,layer,self.comboBox_field.currentIndex() if self.comboBox_field.isEnabled() else -1, self.activelayer.crs(), self.rubberband )
        #process part
        if self.activeLayerIsLine():
            fets = iface.activeLayer().selectedFeatures()
            if len(fets)>0 :    #case when a feature is selected
                fet = fets[0]
                buffer, projectedpoints = self.pointprojector.computeProjectedPoints(fet ,self.spinBox_buffer.value())
                if projectedpoints != None:
                    self.pointprojector.visualResultTestLine()
                    self.pointprojector.createMatPlotLibGraph(self.canvas1, self.ax)
            else:    #case when no feature is selected : reset
                self.pointprojector.resetRubberband()
                layer.removeSelection()

    def extractPoints(self):
        """
        Action when extract button is clicked
        Create temp layer with projected and interpolated points
        """
        #create pointprojector class
        layer = self.getLayerByName(self.comboBox.currentText() )
        self.pointprojector = pointProjector(self,layer,self.comboBox_field.currentIndex() if self.comboBox_field.isEnabled() else -1)
        projectedpointstotal=[]
        #process part
        if self.activeLayerIsLine():
            fets = iface.activeLayer().selectedFeatures()
            self.pointprojector.linecrs = iface.activeLayer().crs()
            if len(fets) == 0 : #process all line in layer
                progress = QProgressBar()
                progress.setMaximum(10)
                progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
                progressMessageBar = iface.messageBar().createMessage("Doing something boring...")
                progress.setMaximum(iface.activeLayer().featureCount())
                progressMessageBar.layout().addWidget(progress)
                iface.messageBar().pushWidget(progressMessageBar, iface.messageBar().INFO)
                for fet in iface.activeLayer().getFeatures():
                    progress.setValue(fet.id()) 
                    buffer, projectedpoints = self.pointprojector.computeProjectedPoints(fet ,self.spinBox_buffer.value(),self.spinBox_spatialstep.value())
                    if projectedpoints != None:
                        projectedpointstotal.append([fet.id(),projectedpoints])
            else:   #process selected line in layer
                fet = fets[0]
                buffer, projectedpoints = self.pointprojector.computeProjectedPoints(fet ,self.spinBox_buffer.value(),self.spinBox_spatialstep.value())
                projectedpointstotal.append([fet.id(),projectedpoints])
            
            #Vector layer creation
            type = "Point?crs="+str(layer.crs().authid()) 
            name = 'Interp_'+str(layer.name())
            vl = QgsVectorLayer(type, name, "memory")
            pr = vl.dataProvider()
            vl.startEditing()
            # add fields
            pr.addAttributes([QgsField("PointID", QVariant.Int)])
            pr.addAttributes(layer.fields())
            pr.addAttributes([QgsField("LineID", QVariant.Int), QgsField("PK", QVariant.Double), QgsField("Interp", QVariant.Double) , QgsField("Type", QVariant.String)])
            vl.updateFields()
            #Add features to layer
            for  projectedpointstemp in projectedpointstotal:
                featid = projectedpointstemp[0]
                projectedpoints = projectedpointstemp[1]
                for projectedpoint in projectedpoints:
                    fet = QgsFeature(layer.fields())
                    #set geometry
                    fet.setGeometry(QgsGeometry.fromPoint(QgsPoint(projectedpoint[1],projectedpoint[2])))
                    #set attributes
                    if projectedpoint[8] != None:
                        attribtemp = [projectedpoint[8].id()]
                        attribtemp += projectedpoint[8].attributes()
                    else:
                        attribtemp = [None]*(len(layer.fields()) + 1 )
                    attribtemp.append(int(featid)) 
                    attribtemp.append(projectedpoint[0])
                    attribtemp.append(projectedpoint[5])
                    if projectedpoint[3] == -1 :
                        attribtemp.append( 'interpolated' )
                    else:
                        attribtemp.append( 'projected' )
                    fet.setAttributes( attribtemp )
                    pr.addFeatures([fet])
            vl.commitChanges()
            #show layer
            QgsMapLayerRegistry.instance().addMapLayer(vl)
            #reinit progess bar
            iface.messageBar().clearWidgets()
    
    
    #********************** Tools *******************************************
                
    def getLayerByName(self,name1):
        for layer in QgsMapLayerRegistry.instance().mapLayers().values():
            if name1 == layer.name():
                return layer
                break
        return None
        
    def activeLayerSelectionChanged(self,selected, deselected,clearAndSelect):
        if self.pointprojector != None:
            self.pointprojector.resetRubberband()
        
    def activeLayerIsLine(self):
        layer = iface.activeLayer()
        if layer.type() == 0 and layer.geometryType() == 1:
            return True
        else:
            iface.messageBar().pushMessage("Error", "Choisir une couche vecteur de type ligne", level=QgsMessageBar.CRITICAL, duration=2)
            return False
            
    def updateLayers(self,list1 = None):
        try:
            self.comboBox.currentIndexChanged.disconnect(self.updateFields)
        except Exception, e:
            pass
        try:
            QgsMapLayerRegistry.instance().layersAdded.disconnect(self.updateLayers)
            QgsMapLayerRegistry.instance().layersRemoved.disconnect(self.updateLayers)
        except Exception, e:
            pass
        self.comboBox.clear()
        for layer in QgsMapLayerRegistry.instance().mapLayers().values():
            if layer.type() in [0] and layer.geometryType() == 0 :
                self.comboBox.addItems([str( layer.name() ) ] )
        self.updateFields()
        self.comboBox.currentIndexChanged.connect(self.updateFields)
        QgsMapLayerRegistry.instance().layersAdded.connect(self.updateLayers)
        QgsMapLayerRegistry.instance().layersRemoved.connect(self.updateLayers)
                
    def updateFields(self):
        self.comboBox_field.clear()
        if self.comboBox.currentText() != '':
            layer = self.getLayerByName(self.comboBox.currentText())
            for field in layer.fields():
                self.comboBox_field.addItems([str( field.name() ) ] )
            
    def activePointFields(self, int1):
        if int1 == 0 :
            self.comboBox_field.setEnabled(False)
        else:
            self.comboBox_field.setEnabled(True)
            

    def closeEvent(self, event):
        """
        Actions when closing plugin dock
        """
        try:
            self.comboBox.currentIndexChanged.disconnect(self.updateFields)
        except Exception, e:
            pass
        try:
            self.activelayer.selectionChanged.disconnect(self.activeLayerSelectionChanged)
        except Exception, e:
            pass
        try:
            QgsMapLayerRegistry.instance().layersAdded.disconnect(self.updateLayers)
            QgsMapLayerRegistry.instance().layersRemoved.disconnect(self.updateLayers)
        except Exception, e:
            pass
        self.ax.cla()
        self.rubberband.reset(QGis.Line)
        self.closingPlugin.emit()
        event.accept()

