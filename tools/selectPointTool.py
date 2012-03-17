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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

class selectPointTool(QgsMapTool):

 def __init__(self, canvas, button):
  QgsMapTool.__init__(self,canvas)
  self.canvas = canvas
  self.cursor = QCursor(Qt.CrossCursor)
  self.button = button

 def canvasMoveEvent(self,event):
  self.emit( SIGNAL("moved"), {'x': event.pos().x(), 'y': event.pos().y()} )


 def canvasReleaseEvent(self,event):
  if event.button() == Qt.RightButton:
   self.emit( SIGNAL("rightClicked"), {'x': event.pos().x(), 'y': event.pos().y()} )
  else:
   self.emit( SIGNAL("leftClicked"), {'x': event.pos().x(), 'y': event.pos().y()} )

 def canvasDoubleClickEvent(self,event):
  self.emit( SIGNAL("doubleClicked"), {'x': event.pos().x(), 'y': event.pos().y()} )

 def activate(self):
  QgsMapTool.activate(self)
  self.canvas.setCursor(self.cursor)
  self.button.setCheckable(True)
  self.button.setChecked(True)


 def deactivate(self):
  self.button.setCheckable(False)
  QgsMapTool.deactivate(self)


 def isZoomTool(self):
  return False
