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


#import qgis
from qgis.core import *
from qgis.gui import *
from qgis.utils import *
#import numpy
import numpy as np
#import PyQT
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtCore import SIGNAL, Qt
from PyQt4 import QtCore, QtGui
#imports divers
import math
from shapely.geometry import *
from sys import maxint

PRECISION = 0.01

class pointProjector(): 

    def __init__(self,dialog, pointlayer, interpfield = -1 , linecrs = None, rubberband = None):
        """
        constructor
        """
        self.pointlayer = pointlayer         #the point layer that will be projected
        self.dialog = dialog
        self.interpfield = interpfield       #The index of field of point layer that will be interpolated
        self.projectedpoints = []           #The projected points numpy array
        self.buffergeom = None              #The geom of the buffer
        self.rubberband = rubberband        #the rubberband
        if linecrs != None:                 #The crs of the line layer
            self.linecrs = linecrs
        else:
            self.linecrs = self.pointlayer.crs()
        
    def computeProjectedPoints(self,fet,valbuffer,spatialstep = 0):
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
        """
        #self.dialog.label_info.setText('Starting ...')
        print 'Starting ...'
        
        self.projectedpoints = []
        self.buffergeom = None
        fet = self.changeFetLineCrs(fet)
        geom = fet.geometry()
        polyline = geom.asPolyline()
        polylineshapely = LineString(polyline)
        
        #Select points in buffer
        if self.pointlayer != None:
            
            self.buffergeom = geom.buffer(valbuffer,10)
            buffershapely = polylineshapely.buffer(valbuffer)
            #buffer = QgsGeometry.fromWkt(buffershapely.to_wkt() )
            #self.buffergeom = QgsGeometry.fromWkt(buffershapely.to_wkt() )
            
            featsPnt = self.pointlayer.getFeatures(QgsFeatureRequest().setFilterRect(self.buffergeom.boundingBox()))
            compt = 0
            
            for featPnt in featsPnt:
                if compt % 500 == 0 :
                    #self.dialog.label_info.setText('Element ' + str(compt))
                    print 'Element ' + str(compt)
                compt += 1
                
                #iterate preselected point features and perform exact check with current polygon
                #if featPnt.geometry().intersects(self.buffergeom):
                point3 = Point(featPnt.geometry().asPoint())
                distpoint = point3.distance(polylineshapely)
                if distpoint <= valbuffer :
                    #point2,dist1,lenght,segment = self.compute_point(fet,featPnt)
                    distline = polylineshapely.project(point3)
                    pointprojected = polylineshapely.interpolate(distline)
                    
                    if self.interpfield >-1 :
                        interptemp = float(featPnt[self.interpfield])
                    else:
                        interptemp = None
                    
                    #self.projectedpoints.append([lenght,point2.x, point2.y,dist1,segment ,interptemp, featPnt.geometry().asPoint().x(),featPnt.geometry().asPoint().y(),featPnt ])
                    self.projectedpoints.append([distline,pointprojected.x, pointprojected.y,distpoint,0 ,interptemp, featPnt.geometry().asPoint().x(),featPnt.geometry().asPoint().y(),featPnt ])
                    
        self.projectedpoints = np.array(self.projectedpoints)
        #perform postprocess computation
        if len(self.projectedpoints)>0:
            #Remove duplicate points
            #self.dialog.label_info.setText('Removing duplicates ...')
            print 'Removing duplicates ...'
            self.removeDuplicateLenght()    
            #Interpolate points beteen porjected points
            #self.dialog.label_info.setText('Interpoling points ...')
            print 'Interpoling points ...'
            self.interpolateNodeofPolyline(geom)
            if spatialstep > 0 :
                #discretize points
                self.dialog.label_info.setText('Discretizing line ...')
                self.discretizeLine(spatialstep)
            self.dialog.label_info.setText('Finished')
            return self.buffergeom, self.projectedpoints
        else:
            self.dialog.label_info.setText('Finished with no points')
            return self.buffergeom, None
    
    
    def discretizeLine(self,spatialstep):
        """
        discretize self.projectedpoints
        """
        tempprojected = []
        for i, projectedpoint in enumerate(self.projectedpoints) :
            if i == len(self.projectedpoints) -1 :
                break
            else:
                long = self.projectedpoints[i+1][0]-self.projectedpoints[i][0]
                if long > spatialstep:
                    count = int(long/spatialstep)
                    for j in range(1,count +1):
                        interpx = self.projectedpoints[i][1] + (self.projectedpoints[i+1][1] - self.projectedpoints[i][1]  )/long*(spatialstep*j)
                        interpy = self.projectedpoints[i][2] + (self.projectedpoints[i+1][2] - self.projectedpoints[i][2]  )/long*(spatialstep*j)
                        if self.interpfield >-1 :
                            interpz = self.projectedpoints[i][5] + (self.projectedpoints[i+1][5] - self.projectedpoints[i][5]  )/long*(spatialstep*j)
                        else:
                            interpz = None
                        tempprojected.append([self.projectedpoints[i][0] + j * spatialstep ,interpx, interpy,-1,self.projectedpoints[i][4] ,interpz, None,None,None ])
        self.projectedpoints = np.append(self.projectedpoints, tempprojected , axis = 0 )
        self.projectedpoints = self.projectedpoints[self.projectedpoints[:,0].argsort()]

    
    
    def removeDuplicateLenght(self):
        
        projectedpointsfinal = []
        duplicate = []
        leninterp = len(self.projectedpoints)
        
        for i in range(len(self.projectedpoints)):
        
            pointtoinsert = None
            
            if i in duplicate:
                continue
            else:
                mindist = np.absolute(self.projectedpoints[:,0] - self.projectedpoints[i,0])
                mindeltaalti = np.absolute(self.projectedpoints[:,5] - self.projectedpoints[i,5])
                mindistindex = np.where(mindist < PRECISION)
                
                if False:
                    minalitindex = np.where(mindeltaalti < PRECISION )
                    minindex = np.intersect1d(mindistindex[0],minalitindex[0])
                    #duplicate lenght with same alti : keep only one
                    if len(minindex) <= 1 :
                        #pointtoinsert = projectedpoints[i]
                        projectedpointsfinal.append(self.projectedpoints[i])
                    else:
                        duplicate += minindex.tolist()
                        #pointtoinsert = projectedpoints[i]
                        projectedpointsfinal.append(self.projectedpoints[i])
                        
                    #duplicate lenght with different alti : keep the closest
                    mindistindex = np.setdiff1d(mindistindex[0],minindex,assume_unique=True)
                    #TO DO
                        
                else:
                    #insert closest point
                    closestindex = np.argmin(self.projectedpoints[mindistindex[0],3])
                    projectedpointsfinal.append(self.projectedpoints[mindistindex[0][closestindex]])
                    duplicate += mindistindex[0].tolist()

                
                
                
                    
        self.projectedpoints = np.array(projectedpointsfinal)
        self.projectedpoints = self.projectedpoints[self.projectedpoints[:,0].argsort()]
        #return projectedpoints
        
        
        
    def removeDuplicateLenght2(self):
        """
        remove points with same pk of self.projectedpoints
        """
        workaray = self.projectedpoints[:,0].tolist()
        duplicatevalues =  set([x for x in workaray if workaray.count(x) > 1])
        while len(duplicatevalues)>0:
            for i,duplicatevaluetemp in enumerate(duplicatevalues):
                if i ==0:
                    duplicatevalue = duplicatevaluetemp
                    break
            equalsvalueindex = np.where(np.array(workaray) == duplicatevalue)
            nearestelem = self.projectedpoints[equalsvalueindex[0]][0]
            for elem in self.projectedpoints[equalsvalueindex]:
                if elem[3] < nearestelem[3]:
                    nearestelem = elem
            self.projectedpoints = np.delete(self.projectedpoints,equalsvalueindex,axis = 0)
            self.projectedpoints = np.append(self.projectedpoints, [nearestelem], axis = 0 )
        
            workaray = self.projectedpoints[:,0].tolist()
            duplicatevalues =  set([x for x in workaray if workaray.count(x) > 1])
        self.projectedpoints = self.projectedpoints[self.projectedpoints[:,0].argsort()]
        #return projectedpoints
        
     
    def interpolateNodeofPolyline(self,geom):
        """
        projectedpoints : array [[lenght, xprojected ,yprojected ,dist from origignal point, segment of polyline on witch it's projected, atribute (z), xoriginal point, yoriginal point ,original point feature], ... ]
        """
        polyline = geom.asPolyline()
        #print 'interp ' + str(len(polyline))
        self.projectedpoints = self.projectedpoints[self.projectedpoints[:,0].argsort()]

        lenpoly = 0
        
        #Write fist and last element
        if self.projectedpoints[0][0] != 0:
            self.projectedpoints = np.append(self.projectedpoints,[[0,polyline[0].x(), polyline[0].y(), -1,0,self.projectedpoints[0][5],polyline[0].x(), polyline[0].y(),self.projectedpoints[0][8] ]], axis = 0)
            self.projectedpoints = self.projectedpoints[self.projectedpoints[:,0].argsort()]
        if self.projectedpoints[-1][0] != geom.length():
            self.projectedpoints = np.append(self.projectedpoints,[[geom.length(),polyline[-1].x(), polyline[-1].y(), -1,len(polyline)-2,self.projectedpoints[-1][5],polyline[-1].x(), polyline[-1].y(),self.projectedpoints[0][8] ]], axis = 0)
            self.projectedpoints = self.projectedpoints[self.projectedpoints[:,0].argsort()]
        
        projectedpointsinterp = []
        polylineshapely = LineString(polyline)
        
        for i,point in enumerate(polyline):
            if i == 0:
                continue
            elif i == len(polyline) -1 :  
                break
            else:
                if i%100 == 0 :
                    print 'interpoling ' + str(i)
                pointshapely = Point(point[0],point[1])
                lenpoly = polylineshapely.project(pointshapely)

                if min(abs(self.projectedpoints[:,0] - lenpoly)) < PRECISION :
                    continue
                else:
                    temp1 = self.interpolatePoint(point,polyline,self.projectedpoints)
                    if temp1 != None :
                        projectedpointsinterp.append( temp1 )
        
        temp = self.projectedpoints.tolist() + projectedpointsinterp
        self.projectedpoints = np.array(temp)
        
        self.projectedpoints = self.projectedpoints[self.projectedpoints[:,0].argsort()]

        #return projectedpoints
     
    def interpolatePoint(self,point,polyline,projectedpoints):
    
        pointshapely = Point(point[0],point[1])
        polylineshapely = LineString(polyline)
        lenpoly = polylineshapely.project(pointshapely)
        
        previouspointindex = np.max(np.where(projectedpoints[:,0]<=lenpoly)[0])
        nextpointindex = np.min(np.where(projectedpoints[:,0]>=lenpoly)[0])
        
        lentot = projectedpoints[nextpointindex][0] - projectedpoints[previouspointindex][0]
        if lentot>0:
            lentemp = lenpoly  - projectedpoints[previouspointindex][0]
            z = projectedpoints[previouspointindex][5] + ( projectedpoints[nextpointindex][5] - projectedpoints[previouspointindex][5] )/ lentot * lentemp
            return [lenpoly, point[0], point[1], -1, None ,z,point[0], point[1], None ]
        else :
            return None
     
    def interpolateNodeofPolyline2(self,geom):
        """
        add points to self.projectedpoints for the nodes of the line
        """
        polyline = geom.asPolyline()
        self.projectedpoints = self.projectedpoints[self.projectedpoints[:,0].argsort()]
        lenpoly = 0
        #Write fist and last element
        if self.projectedpoints[0][0] != 0:
            self.projectedpoints = np.append(self.projectedpoints,[[0,polyline[0].x(), polyline[0].y(), -1,0,self.projectedpoints[0][5],polyline[0].x(), polyline[0].y(),self.projectedpoints[0][8] ]], axis = 0)
            self.projectedpoints = self.projectedpoints[self.projectedpoints[:,0].argsort()]
        if self.projectedpoints[-1][0] != geom.length():
            self.projectedpoints = np.append(self.projectedpoints,[[geom.length(),polyline[-1].x(), polyline[-1].y(), -1,len(polyline)-2,self.projectedpoints[-1][5],polyline[-1].x(), polyline[-1].y(),self.projectedpoints[0][8] ]], axis = 0)
            self.projectedpoints = self.projectedpoints[self.projectedpoints[:,0].argsort()]
        #Compute points inside the line
        for i,point in enumerate(polyline):
            if i == 0:
                continue
            elif i == len(polyline) -1 :  
                break
            else:
                lenpoly += ( (polyline[i].x() - polyline[i-1].x() )**2 + (polyline[i].y() - polyline[i-1].y() )**2  )**0.5
                #search if a point exist on the node - if true skip :
                if len(np.where(self.projectedpoints[:,0] == lenpoly)[0]) > 0 :
                    continue
                else:
                    #find previous and next real point index
                    previouspointindex = np.max(np.where(self.projectedpoints[:,0]<=lenpoly)[0])
                    semgmentmin = int(self.projectedpoints[previouspointindex][4])
                    nextpointindex = np.min(np.where(self.projectedpoints[:,0]>=lenpoly)[0])
                    semgmentmax = int(self.projectedpoints[nextpointindex][4])
                    #find total lenght between wo real points
                    lentot = ( (polyline[semgmentmin+1].x() - self.projectedpoints[previouspointindex][1] )**2 + (polyline[semgmentmin+1].y() - self.projectedpoints[previouspointindex][2] )**2  )**0.5
                    lentemp = lentot
                    for j in range(semgmentmin +1 ,semgmentmax ):
                        if j == i :
                            lentemp = lentot
                        lentot += ( (polyline[j+1].x() - polyline[j].x() )**2 + (polyline[j+1].y() - polyline[j].y() )**2  )**0.5
                    lentot += ( ( self.projectedpoints[nextpointindex][1] - polyline[semgmentmax].x() )**2 + ( self.projectedpoints[nextpointindex][2] - polyline[semgmentmax].y() )**2  )**0.5
                    #"interpolate"
                    if self.interpfield >-1 :
                        z = self.projectedpoints[previouspointindex][5] + ( self.projectedpoints[nextpointindex][5] - self.projectedpoints[previouspointindex][5] )/ lentot * lentemp
                    else:
                        z = None
                    self.projectedpoints = np.append(self.projectedpoints,[[lenpoly, point.x(), point.y(), -1, i,z,polyline[i].x(), polyline[i].y(), None ]], axis = 0)
                    self.projectedpoints = self.projectedpoints[self.projectedpoints[:,0].argsort()]
        self.projectedpoints = self.projectedpoints[self.projectedpoints[:,0].argsort()]

    def visualResultTestLine(self):
        """
        Draw result of the traitment of selected line with a rubberband
        """
        self.resetRubberband()
        if  self.projectedpoints != None:
            featuretoselect =[ projectedpoint.id() for projectedpoint in self.projectedpoints[:,8] if projectedpoint != None]
            self.pointlayer.setSelectedFeatures(featuretoselect)
            self.drawProjectedPointsonRubberband()
        else:
            self.pretelemac.rubberband.reset(QGis.Line)
            
    
    def drawProjectedPointsonRubberband(self):
        xform = QgsCoordinateTransform(self.pointlayer.crs(), iface.mapCanvas().mapRenderer().destinationCrs())
        if self.buffergeom != None:
            xformbufferline = []
            bufferline = self.buffergeom.convertToType(QGis.Line)
            for point in bufferline.asPolyline():
                xformbufferline.append(xform.transform(QgsPoint( point[0],point[1] ) ))
            self.rubberband.addGeometry(QgsGeometry.fromPolyline( xformbufferline) ,None)
        for point in self.projectedpoints:
            x1,y1 = point[1], point[2]
            x2,y2 = point[6], point[7]
            self.rubberband.addGeometry(QgsGeometry.fromPolyline([xform.transform( QgsPoint(x1,y1) ), xform.transform( QgsPoint(x2,y2) ) ]),None)
                                                                                 
    def createMatPlotLibGraph(self,canvas1, ax1):
        ax1.cla()
        if self.interpfield >-1 :
            ax1.grid(color='0.5', linestyle='-', linewidth=0.5)
            ax1.plot(self.projectedpoints[:,0], self.projectedpoints[:,5],linewidth = 3, visible = True)
            canvas1.draw()
        else:
            ax1.grid(color='0.5', linestyle='-', linewidth=0.5)
            canvas1.draw()
                                                                                 
    def resetRubberband(self):
        try:
            self.rubberband.reset(QGis.Line)
        except Exception, e:
            pass
        self.pointlayer.removeSelection()
    
    def changeFetLineCrs(self,fetline):
        geom = fetline.geometry().asPolyline()
        xform1 = QgsCoordinateTransform(self.linecrs, self.pointlayer.crs())
        geomtransf = []
        for point in geom:
            geomtransf.append(xform1.transform(point))
        fetline.setGeometry( QgsGeometry.fromPolyline( geomtransf ))
        return fetline
        
        
     
     
    """"
    #***************** Core projection algorithm
    
    def compute_point(self,line1,point1):
        if point1.geometry().wkbType()==1:
            point =Point(point1.geometry().asPoint().x(),point1.geometry().asPoint().y())
        if line1.geometry().wkbType()==2:
            line = LineString(line1.geometry().asPolyline())
        nearest_point, min_dist ,lenghtfromstart ,segment= self.Closest_point(line,point)
        return (nearest_point, min_dist,lenghtfromstart,segment )
    
    # pairs iterator:
    # http://stackoverflow.com/questions/1257413/1257446#1257446
    def pairs(self,lst):
        i = iter(lst)
        first = prev = i.next()
        for item in i:
            yield prev, item
            prev = item
        #yield item, first

    # these methods rewritten from the C version of Paul Bourke's
    # geometry computations:
    # http://local.wasp.uwa.edu.au/~pbourke/geometry/pointline/
    def magnitude(self,p1, p2):
        vect_x = p2.x - p1.x
        vect_y = p2.y - p1.y
        return math.sqrt(vect_x**2 + vect_y**2)

    def intersect_point_to_line(self,point, line_start, line_end):
        line_magnitude =  self.magnitude(line_end, line_start)
        u = ((point.x - line_start.x) * (line_end.x - line_start.x) +
             (point.y - line_start.y) * (line_end.y - line_start.y)) \
             / (line_magnitude ** 2)

        # closest point does not fall within the line segment, 
        # take the shorter distance to an endpoint
        if u < 0.00001 or u > 1:
            ix = self.magnitude(point, line_start)
            iy = self.magnitude(point, line_end)
            if ix > iy:
                return line_end
            else:
                return line_start
        else:
            ix = line_start.x + u * (line_end.x - line_start.x)
            iy = line_start.y + u * (line_end.y - line_start.y)
            return Point([ix, iy])

    def Closest_point(self,polygon,point):
        nearest_point = None
        min_dist = maxint
        lenght = []
        for i,coord in enumerate(polygon.coords):
            if i == len(polygon.coords)-1:
                break
            line_start = Point(polygon.coords[i])
            line_end = Point(polygon.coords[i+1])
            lenght.append( ( (line_start.x-line_end.x)**2+(line_start.y-line_end.y )**2)**0.5 )
            intersection_point = self.intersect_point_to_line(point, line_start, line_end)
            cur_dist =  self.magnitude(point, intersection_point)
            if cur_dist < min_dist:
                min_dist = cur_dist
                nearest_point = intersection_point
                lenghtfrompreviouspoint = ((line_start.x-nearest_point.x)**2+(line_start.y-nearest_point.y )**2)**0.5
                segmentmin = i
        lenghtfromstart = 0
        for j in range(segmentmin):
            lenghtfromstart += lenght[j]
        lenghtfromstart += lenghtfrompreviouspoint
        #print "Closest point found at: %s, with a distance of %.2f units." %  (nearest_point, min_dist)
        return (nearest_point, min_dist,lenghtfromstart,segmentmin)
    """

