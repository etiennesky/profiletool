#/***************************************************************************
# ProfileTool
# 
# ProfileTool
#                             -------------------
#        begin                : 2012-03-03
#        copyright            : (C) 2012 by patricev
#        email                : XXX
# ***************************************************************************/
# 
#/***************************************************************************
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation; either version 2 of the License, or     *
# *   (at your option) any later version.                                   *
# *                                                                         *
# ***************************************************************************/
# Makefile for a PyQGIS plugin 
PLUGINNAME = profiletool
PY_FILES = doProfile.py profilebase.py __init__.py  profilePlugin.py selectPointTool.py
EXTRAS = profileIcon.png Metadata.txt
UI_FILES = profilebase.py
RESOURCE_FILES = resources.py

default: compile

%.py : %.qrc
	pyrcc4 -o $@  $<

%.py : %.ui
	pyuic4 -o $@ $<

compile: $(UI_FILES) $(RESOURCE_FILES)

# The deploy  target only works on unix like operating system where
# the Python plugin directory is located at:
# $HOME/.qgis/python/plugins
deploy: compile
	mkdir -p $(HOME)/.qgis/python/plugins/$(PLUGINNAME)
	cp -vf $(PY_FILES) $(HOME)/.qgis/python/plugins/$(PLUGINNAME)
	cp -vf $(UI_FILES) $(HOME)/.qgis/python/plugins/$(PLUGINNAME)
	cp -vf $(RESOURCE_FILES) $(HOME)/.qgis/python/plugins/$(PLUGINNAME)
	cp -vf $(EXTRAS) $(HOME)/.qgis/python/plugins/$(PLUGINNAME)

