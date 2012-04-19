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
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
# 
#---------------------------------------------------------------------

def name():
 return "Profile Tool"

def description():
 return "Plots terrain profile"

def version():
 return "Version 3.4.0"

def qgisMinimumVersion():
  return '1.6'

def authorName():
  return 'Borys Jurgiel - Patrice Verchere'

def homepage():
  return 'http://hub.qgis.org/projects/profiletool/wiki'

def classFactory(iface):
 from profileplugin import ProfilePlugin
 return ProfilePlugin(iface)
