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
"""
from PyQt4.QtCore import *
from PyQt4.QtGui import *
"""
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
try:
    from qgis.PyQt.QtWidgets import *
except:
    pass

from .plottingtool import *
from .utils import isProfilable


class TableViewTool(QObject):
    
    layerAddedOrRemoved = pyqtSignal() # Emitted when a new layer is added

    def addLayer(self , iface, mdl, layer1 = None):
        if layer1 == None:
            templist=[]
            j=0
            # Ask the layer by a input dialog 
            for i in range(0, iface.mapCanvas().layerCount()):
                donothing = False
                layer = iface.mapCanvas().layer(i)
                if isProfilable(layer):
                    for j in range(0, mdl.rowCount()):
                        if str(mdl.item(j,2).data(Qt.EditRole)) == str(layer.name()):
                            donothing = True
                else:
                    donothing = True
                    
                if donothing == False:
                    templist +=  [[layer, layer.name()]]
                        
            if len(templist) == 0:
                QMessageBox.warning(iface.mainWindow(), "Profile tool", "No raster to add")
                return
            else:    
                testqt, ok = QInputDialog.getItem(iface.mainWindow(), "Layer selector", "Choose layer", [templist[k][1] for k in range( len(templist) )], False)
                if ok:
                    for i in range (0,len(templist)):
                        if templist[i][1] == testqt:
                            layer2 = templist[i][0]
                else:
                    return
        else : 
            if isProfilable(layer1):
                layer2 = layer1
            else:
                QMessageBox.warning(iface.mainWindow(), "Profile tool", "Active layer is not a profilable layer")
                return

        # Ask the Band by a input dialog
        #First, if isProfilable, considerate the real band number (instead of band + 1 for raster)
        if layer2.type() == layer2.PluginLayer and  isProfilable(layer2):
            self.bandoffset = 0
            typename = 'parameter'
        elif layer2.type() == layer2.RasterLayer:
            self.bandoffset = 1
            typename = 'band'
        elif layer2.type() == layer2.VectorLayer:
            self.bandoffset = 0
            typename = 'field'

            
        if layer2.type() == layer2.RasterLayer and layer2.bandCount() != 1:
            listband = []
            for i in range(0,layer2.bandCount()):
                listband.append(str(i+self.bandoffset))
            testqt, ok = QInputDialog.getItem(iface.mainWindow(), typename + " selector", "Choose the " + typename, listband, False)
            if ok :
                choosenBand = int(testqt) - self.bandoffset
            else:
                return 2
        elif layer2.type() == layer2.VectorLayer :
            fieldstemp = [field.name() for field in layer2.fields() ]
            fields = [field.name() for field in layer2.fields() if field.isNumeric()]
            if len(fields)==0:
                QMessageBox.warning(iface.mainWindow(), "Profile tool", "Active layer is not a profilable layer")
                return
            elif len(fields) == 1 :
                choosenBand = fieldstemp.index(fields[0])
                
            else:
                testqt, ok = QInputDialog.getItem(iface.mainWindow(), typename + " selector", "Choose the " + typename, fields, False)
                if ok :
                    choosenBand = fieldstemp.index(testqt)
                else:
                    return 2
            
        else:
            choosenBand = 0

        #Complete the tableview
        row = mdl.rowCount()
        mdl.insertRow(row)
        mdl.setData( mdl.index(row, 0, QModelIndex())  ,True, Qt.CheckStateRole)
        mdl.item(row,0).setFlags(Qt.ItemIsSelectable) 
        lineColour = Qt.red
        if layer2.type() == layer2.PluginLayer and layer2.LAYER_TYPE == 'crayfish_viewer':
            lineColour = Qt.blue
        mdl.setData( mdl.index(row, 1, QModelIndex())  ,QColor(lineColour) , Qt.BackgroundRole)
        mdl.item(row,1).setFlags(Qt.NoItemFlags) 
        mdl.setData( mdl.index(row, 2, QModelIndex())  ,layer2.name())
        mdl.item(row,2).setFlags(Qt.NoItemFlags) 
        mdl.setData( mdl.index(row, 3, QModelIndex())  ,choosenBand + self.bandoffset)
        mdl.item(row,3).setFlags(Qt.NoItemFlags) 

        if layer2.type() == layer2.VectorLayer :
            #mdl.setData( mdl.index(row, 4, QModelIndex())  ,QVariant(100.0))
            mdl.setData( mdl.index(row, 4, QModelIndex())  ,100.0)
            #mdl.item(row,3).setFlags(Qt.NoItemFlags) 
        else:
            mdl.setData( mdl.index(row, 4, QModelIndex())  ,'')
            mdl.item(row,4).setFlags(Qt.NoItemFlags) 
            
            
        mdl.setData( mdl.index(row, 5, QModelIndex())  ,layer2)
        mdl.item(row,5).setFlags(Qt.NoItemFlags)
        self.layerAddedOrRemoved.emit()
        
        
    def removeLayer(self, mdl, index):
            try:
                mdl.removeRow(index)
                self.layerAddedOrRemoved.emit()
            except:
                return

    def chooseLayerForRemoval(self, iface, mdl):
        
        if mdl.rowCount() < 2:
            if mdl.rowCount() == 1:
                return 0
            return None

        list1 = []
        for i in range(0,mdl.rowCount()):
            list1.append(str(i +1) + " : " + mdl.item(i,2).data(Qt.EditRole))
        testqt, ok = QInputDialog.getItem(iface.mainWindow(), "Layer selector", "Choose the Layer", list1, False)
        if ok:
            for i in range(0,mdl.rowCount()):
                if testqt == (str(i+1) + " : " + mdl.item(i,2).data(Qt.EditRole)):
                    return i
        return None
        
    def onClick(self, iface, wdg, mdl, plotlibrary, index1):                    #action when clicking the tableview
        temp = mdl.itemFromIndex(index1)
        if index1.column() == 1:                #modifying color
            name = ("%s#%d") % (mdl.item(index1.row(),2).data(Qt.EditRole), mdl.item(index1.row(),3).data(Qt.EditRole))
            color = QColorDialog().getColor(temp.data(Qt.BackgroundRole))
            mdl.setData( mdl.index(temp.row(), 1, QModelIndex())  ,color , Qt.BackgroundRole)
            PlottingTool().changeColor(wdg, plotlibrary, color, name)
        elif index1.column() == 0:                #modifying checkbox
            #name = mdl.item(index1.row(),2).data(Qt.EditRole)   
            name = ("%s#%d") % (mdl.item(index1.row(),2).data(Qt.EditRole), mdl.item(index1.row(),3).data(Qt.EditRole))
            booltemp = temp.data(Qt.CheckStateRole)
            if booltemp == True:
                booltemp = False
            else:
                booltemp = True
            mdl.setData( mdl.index(temp.row(), 0, QModelIndex())  ,booltemp, Qt.CheckStateRole)
            PlottingTool().changeAttachCurve(wdg, plotlibrary, booltemp, name)
        elif False and index1.column() == 4:               
            #name = mdl.item(index1.row(),2).data(Qt.EditRole)   
            name = mdl.item(index1.row(),4).data(Qt.EditRole)
            print(name)
            
        else:
            return

        
