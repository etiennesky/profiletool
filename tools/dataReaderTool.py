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
"""
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.Qt import *

from qgis.core import *
import qgis
import numpy as np

import platform
from math import sqrt
from .utils import isProfilable


class DataReaderTool:

    """def __init__(self):
        self.profiles = None"""

    def dataRasterReaderTool(self, iface1,tool1, profile1, pointstoDraw1, fullresolution1):
        """
        Return a dictionnary : {"layer" : layer read,
                                "band" : band read,
                                "l" : array of computed lenght,
                                "z" : array of computed z
        """
        #init
        self.tool = tool1                        #needed to transform point coordinates
        self.profiles = profile1                #profile with layer and band to compute
        self.pointstoDraw = pointstoDraw1        #the polyline to compute
        self.iface = iface1                        #QGis interface to show messages in status bar

        layer = self.profiles["layer"]
        choosenBand = self.profiles["band"]

        #Get the values on the lines
        l = []
        z = []
        x = []
        y = []
        lbefore = 0
        for i in range(0,len(self.pointstoDraw)-2):  # work for each segment of polyline

            # for each polylines, set points x,y with map crs (%D) and layer crs (%C)
            pointstoCal1 = self.tool.toLayerCoordinates(self.profiles["layer"] , QgsPoint(self.pointstoDraw[i][0],self.pointstoDraw[i][1]))
            pointstoCal2 = self.tool.toLayerCoordinates(self.profiles["layer"] , QgsPoint(self.pointstoDraw[i+1][0],self.pointstoDraw[i+1][1]))
            x1D = float(self.pointstoDraw[i][0])
            y1D = float(self.pointstoDraw[i][1])
            x2D = float(self.pointstoDraw[i+1][0])
            y2D = float(self.pointstoDraw[i+1][1])
            x1C = float(pointstoCal1.x())
            y1C = float(pointstoCal1.y())
            x2C = float(pointstoCal2.x())
            y2C = float(pointstoCal2.y())
            #lenght between (x1,y1) and (x2,y2)
            tlC = sqrt (((x2C-x1C)*(x2C-x1C)) + ((y2C-y1C)*(y2C-y1C)))
            #Set the res of calcul
            try:
                res = min(self.profiles["layer"].rasterUnitsPerPixelX(),self.profiles["layer"].rasterUnitsPerPixelY()) * tlC / max(abs(x2C-x1C), abs(y2C-y1C))    # res depend on the angle of ligne with normal
            except ZeroDivisionError:
                res = min(self.profiles["layer"].rasterUnitsPerPixelX(),self.profiles["layer"].rasterUnitsPerPixelY()) * 1.2
            #enventually use bigger step, wether full res is selected or not
            steps = 1000  # max graph width in pixels
            if fullresolution1:
                steps = int(tlC/res)
            else:
                if res != 0 and tlC/res < steps:
                    steps = int(tlC/res)
                else:
                    steps = 1000

            if steps < 1:
                steps = 1
            # calculate dx, dy and dl for one step
            dxD = (x2D - x1D) / steps
            dyD = (y2D - y1D) / steps
            dlD = sqrt ((dxD*dxD) + (dyD*dyD))
            dxC = (x2C - x1C) / steps
            dyC = (y2C - y1C) / steps
            #dlC = sqrt ((dxC*dxC) + (dyC*dyC))
            stepp = steps / 10
            if stepp == 0:
                stepp = 1
            progress = "Creating profile: "
            temp = 0
            # reading data
            if i == 0:
                debut = 0
            else:
                debut = 1
            for n in range(debut, steps+1):
                l += [dlD * n + lbefore]
                xC = x1C + dxC * n
                yC = y1C + dyC * n
                attr = 0
                if layer.type() == layer.PluginLayer and isProfilable(layer):
                    ident = layer.identify(QgsPoint(xC,yC))
                    try:
                        attr = float(ident[1].values()[choosenBand])
                    except:
                        pass
                else: #RASTER LAYERS
                    # this code adapted from valuetool plugin
                    ident = layer.dataProvider().identify(QgsPoint(xC,yC), QgsRaster.IdentifyFormatValue )
                    #if ident is not None and ident.has_key(choosenBand+1):
                    if ident is not None and (choosenBand in ident.results()):
                        attr = ident.results()[choosenBand]
                        #if attr is None:
                        #    attr=float("nan")
                        #print(attr)
                        #if layer.dataProvider().isNoDataValue ( choosenBand+1, attr ):
                            #attr = 0
                #print "Null cell value catched as zero!"  # For none values, profile height = 0. It's not elegant...

                z += [attr]
                x += [xC]
                y += [yC]
                temp = n
                if n % stepp == 0:
                    progress += "|"
                    self.iface.mainWindow().statusBar().showMessage(progress)
            lbefore = l[len(l)-1]
        #End of polyline analysis
        #filling the main data dictionary "profiles"
        self.profiles["l"] = l
        self.profiles["z"] = z
        self.profiles["x"] = x
        self.profiles["y"] = y
        self.iface.mainWindow().statusBar().showMessage("")

        return self.profiles
        
        
    def dataVectorReaderTool(self, iface1,tool1, profile1, pointstoDraw1, valbuf1):
        """
        compute the projected points
        return :
            self.buffergeom : the qgsgeometry of the buffer
            self.projectedpoints : [..., [(point caracteristics : )
                                          #index : descripion
                                          #0 : the pk of the projected point relative to line
                                          #1 : the x coordinate of the projected point
                                          #2 : the y coordinate of the projected point
                                          #3 : the lenght between original point and projected point else -1 if interpolated
                                          #4 : the segment of the polyline on which the point is projected
                                          #5 : the interp value if interpfield>-1, else None
                                          #6 : the x coordinate of the original point if the point is not interpolated, else None
                                          #6 : the y coordinate of the original point if the point is not interpolated, else None
                                          #6 : the feature the original point if the point is not interpolated, else None],
                                           ...]
        Return a dictionnary : {"layer" : layer read,
                                "band" : band read,
                                "l" : array of computed lenght,
                                "z" : array of computed z
                                           
                                           
        """
        valbuffer = valbuf1
        projectedpoints = []
        buffergeom = None

        sourceCrs = QgsCoordinateReferenceSystem( qgis.utils.iface.mapCanvas().mapSettings().destinationCrs() )
        destCrs = QgsCoordinateReferenceSystem(profile1["layer"].crs())
        xform = QgsCoordinateTransform(sourceCrs, destCrs)
        
        geom =  qgis.core.QgsGeometry.fromPolyline([QgsPoint(point[0], point[1]) for point in pointstoDraw1])
        geominlayercrs = qgis.core.QgsGeometry(geom)
        
        tempresult = geominlayercrs.transform(xform)
        
        buffergeom = geom.buffer(valbuffer,12)
        buffergeominlayercrs = qgis.core.QgsGeometry(buffergeom)
        tempresult = buffergeominlayercrs.transform(xform)
        
        featsPnt = profile1["layer"].getFeatures(QgsFeatureRequest().setFilterRect(buffergeominlayercrs.boundingBox()))
        
        for featPnt in featsPnt:
            #iterate preselected point features and perform exact check with current polygon
            point3 = featPnt.geometry()
            distpoint = geominlayercrs.distance(point3)
            if distpoint <= valbuffer :
                distline = geominlayercrs.lineLocatePoint(point3)
                pointprojected = geominlayercrs.interpolate(distline)
                if profile1["band"] >-1 :
                    try:
                        interptemp = float(featPnt[profile1["band"]])
                    except:
                        continue
                else:
                    interptemp = None
                projectedpoints.append([distline,pointprojected.asPoint().x(), pointprojected.asPoint().y(),distpoint,0 ,interptemp, featPnt.geometry().asPoint().x(),featPnt.geometry().asPoint().y(),featPnt ])
                    
        projectedpoints = np.array(projectedpoints)
        
        
        #perform postprocess computation
        
        if len(projectedpoints)>0:
            #remove duplicates
            projectedpoints = self.removeDuplicateLenght(projectedpoints)
            #interpolate value at nodes of polyline
            projectedpoints = self.interpolateNodeofPolyline(geominlayercrs,projectedpoints)
        
        
        
        #preparing return value
        profile={}
        profile["layer"] = profile1["layer"]
        profile["band"] = profile1["band"]
        profile['l'] = [projectedpoint[0] for projectedpoint in projectedpoints]
        profile['z'] = [projectedpoint[5] for projectedpoint in projectedpoints]
        profile['x'] = [projectedpoint[1] for projectedpoint in projectedpoints]
        profile['y'] = [projectedpoint[2] for projectedpoint in projectedpoints]
        
        multipoly = qgis.core.QgsGeometry.fromMultiPolyline([[xform.transform(QgsPoint(projectedpoint[1], projectedpoint[2]), qgis.core.QgsCoordinateTransform.ReverseTransform) , 
                                                              xform.transform(QgsPoint(projectedpoint[6], projectedpoint[7]), qgis.core.QgsCoordinateTransform.ReverseTransform)  ] for projectedpoint in projectedpoints])
        
        
        return profile, buffergeom, multipoly
        



    def removeDuplicateLenght(self,projectedpoints):
        
        projectedpointsfinal = []
        duplicate = []
        leninterp = len(projectedpoints)
        PRECISION = 0.01
        
        for i in range(len(projectedpoints)):
            pointtoinsert = None
            if i in duplicate:
                continue
            else:
                mindist = np.absolute(projectedpoints[:,0] - projectedpoints[i,0])
                mindeltaalti = np.absolute(projectedpoints[:,5] - projectedpoints[i,5])
                mindistindex = np.where(mindist < PRECISION)
                
                if False:
                    minalitindex = np.where(mindeltaalti < PRECISION )
                    minindex = np.intersect1d(mindistindex[0],minalitindex[0])
                    #duplicate lenght with same alti : keep only one
                    if len(minindex) <= 1 :
                        projectedpointsfinal.append(projectedpoints[i])
                    else:
                        duplicate += minindex.tolist()
                        projectedpointsfinal.append(projectedpoints[i])
                        
                    #duplicate lenght with different alti : keep the closest
                    mindistindex = np.setdiff1d(mindistindex[0],minindex,assume_unique=True)
                else:
                    #insert closest point
                    closestindex = np.argmin(projectedpoints[mindistindex[0],3])
                    projectedpointsfinal.append(projectedpoints[mindistindex[0][closestindex]])
                    duplicate += mindistindex[0].tolist()
                    
        projectedpoints = np.array(projectedpointsfinal)
        projectedpoints = projectedpoints[projectedpoints[:,0].argsort()]
        return projectedpoints

        
    #def interpolateNodeofPolyline(self,geom):
    def interpolateNodeofPolyline(self,geom,projectedpoints):
        """
        projectedpoints : array [[lenght, xprojected ,yprojected ,dist from origignal point, segment of polyline on witch it's projected, atribute (z), xoriginal point, yoriginal point ,original point feature], ... ]
        """
        PRECISION = 0.01
        polyline = geom.asPolyline()
        projectedpoints = projectedpoints[projectedpoints[:,0].argsort()]

        lenpoly = 0
        
        #Write fist and last element if no value
        if projectedpoints[0][0] != 0:
            projectedpoints = np.append(projectedpoints,[[0,polyline[0].x(), polyline[0].y(), -1,0,projectedpoints[0][5],polyline[0].x(), polyline[0].y(),projectedpoints[0][8] ]], axis = 0)
            projectedpoints = projectedpoints[projectedpoints[:,0].argsort()]
        if projectedpoints[-1][0] != geom.length():
            projectedpoints = np.append(projectedpoints,[[geom.length(),polyline[-1].x(), polyline[-1].y(), -1,len(polyline)-2,projectedpoints[-1][5],polyline[-1].x(), polyline[-1].y(),projectedpoints[0][8] ]], axis = 0)
            projectedpoints = projectedpoints[projectedpoints[:,0].argsort()]
        
        projectedpointsinterp = []
        
        for i,point in enumerate(polyline):
            if i == 0:
                continue
            elif i == len(polyline) -1 :  
                break
            else:
                vertexpoint = geom.vertexAt(i)
                lenpoly = geom.lineLocatePoint(qgis.core.QgsGeometry.fromPoint(vertexpoint))
                
                if min(abs(projectedpoints[:,0] - lenpoly)) < PRECISION :
                    continue
                else:
                    temp1 = self.interpolatePoint(vertexpoint,geom,projectedpoints)
                    if temp1 != None :
                        projectedpointsinterp.append( temp1 )
                            
        
        temp = projectedpoints.tolist() + projectedpointsinterp
        projectedpoints = np.array(temp)
        
        projectedpoints = projectedpoints[projectedpoints[:,0].argsort()]
        
        return projectedpoints
        
        
    def interpolatePoint(self,vertexpoint,geom,projectedpoints):
    
        lenpoly = geom.lineLocatePoint(qgis.core.QgsGeometry.fromPoint(vertexpoint))
        
        previouspointindex = np.max(np.where(projectedpoints[:,0]<=lenpoly)[0])
        nextpointindex = np.min(np.where(projectedpoints[:,0]>=lenpoly)[0])
        
        lentot = projectedpoints[nextpointindex][0] - projectedpoints[previouspointindex][0]
        if lentot>0:
            lentemp = lenpoly  - projectedpoints[previouspointindex][0]
            z = projectedpoints[previouspointindex][5] + ( projectedpoints[nextpointindex][5] - projectedpoints[previouspointindex][5] )/ lentot * lentemp
            #return [lenpoly, point[0], point[1], -1, None ,z,point[0], point[1], None ]
            return [lenpoly, vertexpoint.x(), vertexpoint.y(), -1, None ,z,vertexpoint.x(), vertexpoint.y(), None ]
        else :
            return None

