# -*- coding: utf-8 -*-
#-----------------------------------------------------------
#
# Profile
# Copyright (C) 2013  Peter Wells
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

import qgis
from qgis.PyQt import QtCore

def isProfilable(layer):
    """
        Returns True if layer is capable of being profiles,
        else returns False
    """
    if int(QtCore.QT_VERSION_STR[0]) == 4 :    #qgis2
        if int(qgis.utils.QGis.QGIS_VERSION.split('.')[0]) == 2 and int(qgis.utils.QGis.QGIS_VERSION.split('.')[1]) < 18 :
            return    (layer.type() == layer.RasterLayer) or \
                    (layer.type() == layer.PluginLayer and layer.LAYER_TYPE == 'crayfish_viewer') or \
                    (layer.type() == layer.PluginLayer and layer.LAYER_TYPE == 'selafin_viewer') 
        elif int(qgis.utils.QGis.QGIS_VERSION.split('.')[0]) == 2 and int(qgis.utils.QGis.QGIS_VERSION.split('.')[1]) >= 18 :
            return    (layer.type() == layer.RasterLayer) or \
                    (layer.type() == layer.PluginLayer and layer.LAYER_TYPE == 'crayfish_viewer') or \
                    (layer.type() == layer.PluginLayer and layer.LAYER_TYPE == 'selafin_viewer') or \
                    (layer.type() == layer.VectorLayer and layer.geometryType() == qgis.core.QGis.Point)
    elif int(QtCore.QT_VERSION_STR[0]) == 5 :    #qgis3
        return    (layer.type() == layer.RasterLayer) or \
                (layer.type() == layer.PluginLayer and layer.LAYER_TYPE == 'crayfish_viewer') or \
                (layer.type() == layer.PluginLayer and layer.LAYER_TYPE == 'selafin_viewer') or \
                (layer.type() == layer.VectorLayer and layer.geometryType() ==  qgis.core.QgsWkbTypes.PointGeometry   )

