import qgis


vl = iface.activeLayer()

crs1 = vl.crs() 
crs2 = iface.mapCanvas().mapSettings().destinationCrs()

dist = qgis.core.QgsDistanceArea()
#dist.setEllipsoid(qgis.core.QgsProject().instance().ellipsoid())
#dist.setEllipsoidalMode(True)
dist.setSourceCrs(crs2)

dist2 = qgis.core.QgsDistanceArea()
#dist2.setEllipsoid(qgis.core.QgsProject().instance().ellipsoid())
#dist2.setEllipsoidalMode(True)
dist2.setSourceCrs(crs1)

print(dist.convertLengthMeasurement(1.0, crs1.mapUnits()) )
print(dist2.convertLengthMeasurement(1.0, crs2.mapUnits()) )

